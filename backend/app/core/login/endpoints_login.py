import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.login import schemas_login
from app.core.utils.config import Settings
from app.core.utils.security import (
    authenticate_user,
    create_access_token,
)
from app.dependencies import (
    get_db,
    get_settings,
    is_user,
)
from app.types.module import CoreModule
from app.types.scopes_type import ScopeType
from app.core.users import models_users, schemas_users
from datetime import UTC, datetime, timedelta

import aiofiles
from fastapi import (
    Body,
)
from sqlalchemy.exc import IntegrityError

from app.core.users import cruds_users
from app.core.users.type_users import AccountType
from app.core.utils import security
from app.dependencies import (
    get_request_id,
)
from app.types import standard_responses
from app.utils.mail.mailworker import send_email
from app.utils.tools import (
    create_and_send_email_migration,
)

router = APIRouter(tags=["Auth"])

core_module = CoreModule(
    tag="Login",
    router=router,
)

templates = Jinja2Templates(directory="assets/templates")

# We could maybe use hyperion.security
rttrail_access_logger = logging.getLogger("rttrail.access")
rttrail_security_logger = logging.getLogger("rttrail.security")


@router.post(
    "/login/access-token",
    response_model=schemas_login.AccessToken,
    status_code=200,
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Ask for a JWT access token using oauth password flow.

    *username* and *password* must be provided

    Note: the request body needs to use **form-data** and not json.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    # We put the user id in the subject field of the token.
    # The subject `sub` is a JWT registered claim name, see https://datatracker.ietf.org/doc/html/rfc7519#section-4.1
    data = schemas_login.TokenData(sub=str(user.id), scopes=ScopeType.auth)
    access_token = create_access_token(settings=settings, data=data)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/test-token", response_model=schemas_users.User)
def test_token(current_user: models_users.User = Depends(is_user)):
    """
    Test access token
    """
    return current_user


@router.post(
    "/login/reset-password",
    response_model=standard_responses.Result,
    status_code=201,
)
async def reset_password(
    reset_password_request: schemas_login.ResetPassword,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset the user password, using a **reset_token** provided by `/users/recover` endpoint.
    """
    recover_request = await cruds_users.get_recover_request_by_reset_token(
        db=db,
        reset_token=reset_password_request.reset_token,
    )
    if recover_request is None:
        raise HTTPException(status_code=404, detail="Invalid reset token")

    # We need to make sure the unconfirmed user is still valid
    if recover_request.expire_on < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="Expired reset token")

    new_password_hash = security.get_password_hash(reset_password_request.new_password)
    await cruds_users.update_user_password_by_id(
        db=db,
        user_id=recover_request.user_id,
        new_password_hash=new_password_hash,
    )

    # As the user has reset its password, all other recovery requests can be deleted from the table
    await cruds_users.delete_recover_request_by_email(
        db=db,
        email=recover_request.email,
    )

    return standard_responses.Result()


@router.post(
    "/login/migrate-mail",
    status_code=204,
)
async def migrate_mail(
    mail_migration: schemas_login.MailMigration,
    db: AsyncSession = Depends(get_db),
    user: models_users.User = Depends(is_user()),
    settings: Settings = Depends(get_settings),
):
    """
    This endpoint will send a confirmation code to the user's new email address. He will need to use this code to confirm the change with `/users/confirm-mail-migration` endpoint.
    """

    existing_user = await cruds_users.get_user_by_email(
        db=db,
        email=mail_migration.new_email,
    )
    if existing_user is not None:
        rttrail_security_logger.info(
            f"Email migration: There is already an account with the email {mail_migration.new_email}",
        )
        if settings.SMTP_ACTIVE:
            migration_content = templates.get_template(
                "migration_mail_already_used.html",
            ).render({})
            send_email(
                recipient=mail_migration.new_email,
                subject="MyECL - Confirm your new email adresse",
                content=migration_content,
                settings=settings,
            )
        return

    await create_and_send_email_migration(
        user_id=str(user.id),
        new_email=mail_migration.new_email,
        old_email=user.email,
        db=db,
        settings=settings,
    )


@router.get(
    "/login/migrate-mail-confirm",
    status_code=200,
)
async def migrate_mail_confirm(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    This endpoint will update the user new email address.
    The user will need to use the confirmation code sent by the `/users/migrate-mail` endpoint.
    """

    migration_object = await cruds_users.get_email_migration_code_by_token(
        confirmation_token=token,
        db=db,
    )

    if migration_object is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid confirmation token for this user",
        )

    existing_user = await cruds_users.get_user_by_email(
        db=db,
        email=migration_object.new_email,
    )
    if existing_user is not None:
        rttrail_security_logger.info(
            f"Email migration: There is already an account with the email {migration_object.new_email}",
        )
        raise HTTPException(
            status_code=400,
            detail=f"There is already an account with the email {migration_object.new_email}",
        )

    user = await cruds_users.get_user_by_id(
        db=db,
        user_id=migration_object.user_id,
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    try:
        await cruds_users.update_user(
            db=db,
            user_id=migration_object.user_id,
            user_update=schemas_users.UserUpdateAdmin(
                email=migration_object.new_email,
            ),
        )
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email migration failed due to database integrity error",
        )
    except Exception as error:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    await cruds_users.delete_email_migration_code_by_token(
        confirmation_token=token,
        db=db,
    )

    async with aiofiles.open(
        "data/core/mail-migration-archives.txt",
        mode="a",
    ) as file:
        await file.write(
            f"{migration_object.user_id},{migration_object.old_email},{migration_object.new_email}\n",
        )

    return "The email address has been successfully updated"


@router.post(
    "/login/change-password",
    response_model=standard_responses.Result,
    status_code=201,
)
async def change_password(
    change_password_request: schemas_login.ChangePassword,
    db: AsyncSession = Depends(get_db),
):
    """
    Change a user password.

    This endpoint will check the **old_password**, see also the `/users/reset-password` endpoint if the user forgot their password.
    """

    user = await security.authenticate_user(
        db=db,
        email=change_password_request.email,
        password=change_password_request.old_password,
    )
    if user is None:
        raise HTTPException(status_code=403, detail="The old password is invalid")

    new_password_hash = security.get_password_hash(change_password_request.new_password)
    await cruds_users.update_user_password_by_id(
        db=db,
        user_id=user.id,
        new_password_hash=new_password_hash,
    )

    return standard_responses.Result()


@router.post(
    "/login/activate",
    response_model=standard_responses.Result,
    status_code=201,
)
async def activate_user(
    user: schemas_users.UserActivate,
    db: AsyncSession = Depends(get_db),
    request_id: str = Depends(get_request_id),
):
    """
    Activate the previously created account.

    **token**: the activation token sent by email to the user

    """
    # We need to find the corresponding user_unconfirmed
    unconfirmed_user = await cruds_users.get_unconfirmed_user_by_activation_token(
        db=db,
        activation_token=user.activation_token,
    )
    if unconfirmed_user is None:
        raise HTTPException(status_code=404, detail="Invalid activation token")

    # We need to make sure the unconfirmed user is still valid
    if unconfirmed_user.expire_on < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="Expired activation token")

    # An account with the same email may exist if:
    # - the user called two times the user creation endpoints and got two activation token
    # - used a first token to activate its account
    # - tries to use the second one
    # Though usually all activation tokens linked to the email should have been deleted when the account was activated
    db_user = await cruds_users.get_user_by_email(db=db, email=unconfirmed_user.email)
    if db_user is not None:
        raise HTTPException(
            status_code=400,
            detail=f"The account with the email {unconfirmed_user.email} is already confirmed",
        )

    confirmed_user = models_users.User(
        id=unconfirmed_user.id,
        email=unconfirmed_user.email,
        account_type=AccountType.user,
        password_hash=unconfirmed_user.password_hash,
        name=user.name,
        created_on=datetime.now(UTC),
        is_active=True,
    )
    # We add the new user to the database
    await cruds_users.create_user(db=db, user=confirmed_user)

    # We remove all unconfirmed users with the same email address
    await cruds_users.delete_unconfirmed_user_by_email(
        db=db,
        email=unconfirmed_user.email,
    )

    rttrail_security_logger.info(
        f"Activate_user: Activated user {confirmed_user.id} (email: {confirmed_user.email}) ({request_id})",
    )

    return standard_responses.Result()


@router.post(
    "/login/recover",
    response_model=standard_responses.Result,
    status_code=201,
)
async def recover_user(
    # We use embed for email parameter: https://fastapi.tiangolo.com/tutorial/body-multiple-params/#embed-a-single-body-parameter
    email: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Allow a user to start a password reset process.

    If the provided **email** corresponds to an existing account, a password reset token will be sent.
    Using this token, the password can be changed with `/users/reset-password` endpoint
    """

    db_user = await cruds_users.get_user_by_email(db=db, email=email)
    if db_user is None:
        if settings.SMTP_ACTIVE:
            reset_content = templates.get_template(
                "reset_mail_does_not_exist.html",
            ).render()
            send_email(
                recipient=email,
                subject="MyECL - reset your password",
                content=reset_content,
                settings=settings,
            )
        else:
            rttrail_security_logger.info(
                f"Reset password failed for {email}, user does not exist",
            )

    else:
        # The user exists, we can send a password reset invitation
        reset_token = security.generate_token()

        recover_request = models_users.UserRecoverRequest(
            email=email,
            user_id=db_user.id,
            reset_token=reset_token,
            created_on=datetime.now(UTC),
            expire_on=datetime.now(UTC)
            + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS),
        )

        await cruds_users.create_user_recover_request(
            db=db,
            recover_request=recover_request,
        )

        if settings.SMTP_ACTIVE:
            reset_content = templates.get_template("reset_mail.html").render()
            send_email(
                recipient=db_user.email,
                subject="MyECL - reset your password",
                content=reset_content,
                settings=settings,
            )
        else:
            rttrail_security_logger.info(
                f"Reset password for {email}",
            )

    return standard_responses.Result()

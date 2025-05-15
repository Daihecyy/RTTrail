import logging
import string
import uuid
from datetime import UTC, datetime, timedelta

import aiofiles
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import cruds_users, models_users, schemas_users
from app.core.users.type_users import AccountType
from app.core.utils import security
from app.core.utils.config import Settings
from app.dependencies import (
    get_db,
    get_request_id,
    get_settings,
    is_user,
)
from app.types import standard_responses
from app.types.content_type import ContentType
from app.types.exceptions import UserWithEmailAlreadyExistError
from app.types.module import CoreModule
from app.utils.mail.mailworker import send_email
from app.utils.tools import (
    create_and_send_email_migration,
    get_file_from_data,
    save_file_as_data,
    sort_user,
)

router = APIRouter(tags=["Users"])

core_module = CoreModule(
    root="users",
    tag="Users",
    router=router,
)

rttrail_error_logger = logging.getLogger("rttrail.error")
rttrail_security_logger = logging.getLogger("rttrail.security")

templates = Jinja2Templates(directory="assets/templates")


@router.get(
    "/users",
    response_model=list[schemas_users.UserSimple],
    status_code=200,
)
async def read_users(
    accountTypes: list[AccountType] = Query(default=[]),
    db: AsyncSession = Depends(get_db),
    user: models_users.User = Depends(is_user(AccountType.admin)),
):
    """
    Return all users from database as a list of `CoreUserSimple`

    **This endpoint is only usable by administrators**
    """
    accountTypes = accountTypes if len(accountTypes) != 0 else list(AccountType)

    users = await cruds_users.get_users(db, included_account_types=accountTypes)
    return users


@router.get(
    "/users/count",
    response_model=int,
    status_code=200,
)
async def count_users(
    db: AsyncSession = Depends(get_db),
    user: models_users.User = Depends(is_user(AccountType.admin)),
):
    """
    Return the number of users in the database

    **This endpoint is only usable by administrators**
    """

    count = await cruds_users.count_users(db)
    return count


@router.get(
    "/users/search",
    response_model=list[schemas_users.UserSimple],
    status_code=200,
)
async def search_users(
    query: str,
    includedAccountTypes: list[AccountType] = Query(default=[]),
    excludedAccountTypes: list[AccountType] = Query(default=[]),
    db: AsyncSession = Depends(get_db),
    user: models_users.User = Depends(is_user),
):
    """
    Search for a user using Jaro_Winkler distance algorithm.
    The `query` will be compared against users name, firstname and nickname.
    Assume that `query` is the beginning of a name, so we can capitalize words to improve results.

    **The user must be authenticated to use this endpoint**
    """

    users = await cruds_users.get_users(
        db,
        included_account_types=includedAccountTypes,
        excluded_account_types=excludedAccountTypes,
    )

    return sort_user(string.capwords(query), users)


@router.get(
    "/users/account-types",
    response_model=list[AccountType],
    status_code=200,
)
async def get_account_types(
    db: AsyncSession = Depends(get_db),
    user: models_users.User = Depends(is_user(AccountType.admin)),
):
    """
    Return all account types hardcoded in the system
    """

    return list(AccountType)


@router.get(
    "/users/me",
    response_model=schemas_users.User,
    status_code=200,
)
async def read_current_user(
    user: models_users.User = Depends(is_user()),
):
    """
    Return `CoreUser` representation of current user

    **The user must be authenticated to use this endpoint**
    """

    return user


@router.post(
    "/users/create",
    response_model=standard_responses.Result,
    status_code=201,
)
async def create_user_by_user(
    user_create: schemas_users.UserCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
    request_id: str = Depends(get_request_id),
):
    """
    Start the user account creation process. The user will be sent an email with a link to activate his account.
    > The received token needs to be sent to the `/users/activate` endpoint to activate the account.

    If the **password** is not provided, it will be required during the activation process. Don't submit a password if you are creating an account for someone else.

    Only admin users can create other **account types**, contact ÉCLAIR for more information.
    """

    # Make sure a confirmed account does not already exist
    db_user = await cruds_users.get_user_by_email(db=db, email=user_create.email)
    if db_user is not None:
        rttrail_security_logger.warning(
            f"Create_user: an user with email {user_create.email} already exists ({request_id})",
        )
        # We will send to the email a message explaining they already have an account and can reset their password if they want.
        if settings.SMTP_ACTIVE:
            account_exists_content = templates.get_template(
                "account_exists_mail.html",
            ).render()
            background_tasks.add_task(
                send_email,
                recipient=user_create.email,
                subject="MyECL - your account already exists",
                content=account_exists_content,
                settings=settings,
            )

        # Fail silently: the user should not be informed that a user with the email address already exist.
        return standard_responses.Result(success=True)

    # There might be an unconfirmed user in the database but its not an issue. We will generate a second activation token.

    await create_user(
        email=user_create.email,
        background_tasks=background_tasks,
        db=db,
        settings=settings,
        request_id=request_id,
    )

    return standard_responses.Result(success=True)


async def create_user(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession,
    settings: Settings,
    request_id: str,
) -> None:
    """
    User creation process. This function is used by both `/users/create` and `/users/admin/create` endpoints
    """
    # Warning: the validation token (and thus user_unconfirmed object) should **never** be returned in the request

    # If an account already exist, we can not create a new one
    db_user = await cruds_users.get_user_by_email(db=db, email=email)
    if db_user is not None:
        raise UserWithEmailAlreadyExistError(email)
    # There might be an unconfirmed user in the database but its not an issue. We will generate a second activation token.

    activation_token = security.generate_token(nbytes=16)

    # Add the unconfirmed user to the unconfirmed_user table

    user_unconfirmed = models_users.UserUnconfirmed(
        id=str(uuid.uuid4()),
        email=email,
        activation_token=activation_token,
        created_on=datetime.now(UTC),
        expire_on=datetime.now(UTC)
        + timedelta(hours=settings.USER_ACTIVATION_TOKEN_EXPIRE_HOURS),
    )

    await cruds_users.create_unconfirmed_user(user_unconfirmed=user_unconfirmed, db=db)

    # After adding the unconfirmed user to the database, we got an activation token that need to be send by email,
    # in order to make sure the email address is valid

    if settings.SMTP_ACTIVE:
        activation_content = templates.get_template("activation_mail.html").render()
        background_tasks.add_task(
            send_email,
            recipient=email,
            subject="MyECL - confirm your email",
            content=activation_content,
            settings=settings,
        )
        rttrail_security_logger.info(
            f"Create_user: Creating an unconfirmed account for {email} ({request_id})",
        )
    else:
        rttrail_security_logger.info(
            f"Create_user: Creating an unconfirmed account for {email} ({request_id})",
        )


@router.post(
    "/users/activate",
    response_model=standard_responses.Result,
    status_code=201,
)
async def activate_user(
    user: schemas_users.UserActivateRequest,
    db: AsyncSession = Depends(get_db),
    request_id: str = Depends(get_request_id),
):
    """
    Activate the previously created account.

    **token**: the activation token sent by email to the user

    **password**: user password, required if it was not provided previously
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

    # Get the account type and school_id from the email
    # A password should have been provided
    password_hash = security.get_password_hash(user.password)

    confirmed_user = models_users.User(
        id=unconfirmed_user.id,
        email=unconfirmed_user.email,
        account_type=AccountType.user,
        password_hash=password_hash,
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
    "/users/make-admin",
    response_model=standard_responses.Result,
    status_code=200,
)
async def make_admin(
    db: AsyncSession = Depends(get_db),
):
    """
    This endpoint is only usable if the database contains exactly one user.
    It will add this user to the `admin` group.
    """
    users = await cruds_users.get_users(db=db)

    if len(users) != 1:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only usable if there is exactly one user in the database",
        )

    try:
        # TODO
        ...
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return standard_responses.Result()


@router.post(
    "/users/recover",
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
            + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS),
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


@router.post(
    "/users/reset-password",
    response_model=standard_responses.Result,
    status_code=201,
)
async def reset_password(
    reset_password_request: schemas_users.ResetPasswordRequest,
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
    "/users/migrate-mail",
    status_code=204,
)
async def migrate_mail(
    mail_migration: schemas_users.MailMigrationRequest,
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
        user_id=user.id,
        new_email=mail_migration.new_email,
        old_email=user.email,
        db=db,
        settings=settings,
    )


@router.get(
    "/users/migrate-mail-confirm",
    status_code=200,
)
async def migrate_mail_confirm(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    This endpoint will updates the user new email address.
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
    "/users/change-password",
    response_model=standard_responses.Result,
    status_code=201,
)
async def change_password(
    change_password_request: schemas_users.ChangePasswordRequest,
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


# We put the following endpoints at the end of the file to prevent them
# from interacting with the previous endpoints
# Ex: /users/activate is interpreted as a user whose id is "activate"


@router.get(
    "/users/{user_id}",
    response_model=schemas_users.User,
    status_code=200,
)
async def read_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    user: models_users.User = Depends(is_user(AccountType.admin)),
):
    """
    Return `CoreUser` representation of user with id `user_id`

    **The user must be authenticated to use this endpoint**
    """

    db_user = await cruds_users.get_user_by_id(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# TODO: readd this after making sure all information about the user has been deleted
# @router.delete(
#    "/users/{user_id}",
#    status_code=204,
## )
# async def delete_user(user_id: str, db: AsyncSession = Depends(get_db), user: models_users.CoreUser = Depends(is_user_in(AccountType.admin))):
#    """Delete user from database by id"""
#    # TODO: WARNING - deleting an user without removing its relations ship in other tables will have unexpected consequences
#
#    await cruds_users.delete_user(db=db, user_id=user_id)


@router.post(
    "/users/me/ask-deletion",
    status_code=204,
)
async def delete_user(
    user: models_users.User = Depends(is_user()),
):
    """
    This endpoint will ask administrators to process to the user deletion.
    This manual verification is needed to prevent data from being deleting for other users
    """
    rttrail_security_logger.info(
        f"User {user.email} - {user.id} has requested to delete their account.",
    )


@router.patch(
    "/users/me",
    status_code=204,
)
async def update_current_user(
    user_update: schemas_users.UserUpdate,
    db: AsyncSession = Depends(get_db),
    user: models_users.User = Depends(is_user()),
):
    """
    Update the current user, the request should contain a JSON with the fields to change (not necessarily all fields) and their new value

    **The user must be authenticated to use this endpoint**
    """

    await cruds_users.update_user(db=db, user_id=user.id, user_update=user_update)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Update failed due to database integrity error",
        )


@router.patch(
    "/users/{user_id}",
    status_code=204,
)
async def update_user(
    user_id: str,
    user_update: schemas_users.UserUpdateAdmin,
    db: AsyncSession = Depends(get_db),
    user: models_users.User = Depends(is_user(AccountType.admin)),
):
    """
    Update an user, the request should contain a JSON with the fields to change (not necessarily all fields) and their new value

    **This endpoint is only usable by administrators**
    """
    db_user = await cruds_users.get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await cruds_users.update_user(db=db, user_id=user_id, user_update=user_update)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Update failed due to database integrity error",
        )


@router.post(
    "/users/me/profile-picture",
    response_model=standard_responses.Result,
    status_code=201,
)
async def create_current_user_profile_picture(
    image: UploadFile = File(...),
    user: models_users.User = Depends(is_user()),
    request_id: str = Depends(get_request_id),
):
    """
    Upload a profile picture for the current user.

    **The user must be authenticated to use this endpoint**
    """

    await save_file_as_data(
        upload_file=image,
        directory="profile-pictures",
        filename=str(user.id),
        request_id=request_id,
        max_file_size=4 * 1024 * 1024,
        accepted_content_types=[
            ContentType.jpg,
            ContentType.png,
            ContentType.webp,
        ],
    )

    return standard_responses.Result(success=True)


@router.get(
    "/users/me/profile-picture",
    response_class=FileResponse,
    status_code=200,
)
async def read_own_profile_picture(
    user: models_users.User = Depends(is_user()),
):
    """
    Get the profile picture of the authenticated user.
    """

    return get_file_from_data(
        directory="profile-pictures",
        filename=str(user.id),
        default_asset="assets/images/default_profile_picture.png",
    )


@router.get(
    "/users/{user_id}/profile-picture",
    response_class=FileResponse,
    status_code=200,
)
async def read_user_profile_picture(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the profile picture of an user.

    Unauthenticated users can use this endpoint (needed for some OIDC services)
    """

    db_user = await cruds_users.get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_file_from_data(
        directory="profile-pictures",
        filename=str(user_id),
        default_asset="assets/images/default_profile_picture.png",
    )

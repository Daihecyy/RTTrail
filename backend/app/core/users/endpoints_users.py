import logging
import string
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
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
from app.types.exceptions import UserWithEmailAlreadyExistError
from app.types.module import CoreModule
from app.utils.mail.mailworker import send_email
from app.utils.tools import (
    get_file_from_data,
    sort_user,
)

router = APIRouter(tags=["Users"])

core_module = CoreModule(
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
    Return all users from database as a list of `UserSimple`

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


@router.post(
    "/users/register",
    response_model=standard_responses.Result,
    status_code=201,
)
async def user_register(
    user_data: schemas_users.UserRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
    request_id: str = Depends(get_request_id),
):
    """
    Register a user
    """

    # Make sure a confirmed account does not already exist
    db_user = await cruds_users.get_user_by_email(db=db, email=user_data.email)
    if db_user is not None:
        rttrail_security_logger.warning(
            f"Create_user: an user with email {user_data.email} already exists ({request_id})",
        )
        # We will send to the email a message explaining they already have an account and can reset their password if they want.
        if settings.SMTP_ACTIVE:
            account_exists_content = templates.get_template(
                "account_exists_mail.html",
            ).render()
            background_tasks.add_task(
                send_email,
                recipient=user_data.email,
                subject="MyECL - your account already exists",
                content=account_exists_content,
                settings=settings,
            )

        # Fail silently: the user should not be informed that a user with the email address already exist.
        return standard_responses.Result(success=True)

    # There might be an unconfirmed user in the database but its not an issue. We will generate a second activation token.

    await create_user(
        user_data=user_data,
        background_tasks=background_tasks,
        db=db,
        settings=settings,
        request_id=request_id,
    )

    return standard_responses.Result(success=True)


async def create_user(
    user_data: schemas_users.UserRegister,
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
    db_user = await cruds_users.get_user_by_email(db=db, email=user_data.email)
    if db_user is not None:
        raise UserWithEmailAlreadyExistError(user_data.email)
    # There might be an unconfirmed user in the database but its not an issue. We will generate a second activation token.

    activation_token = security.generate_token(nbytes=16)

    # Add the unconfirmed user to the unconfirmed_user table
    password_hash = security.get_password_hash(user_data.password)

    user_unconfirmed = models_users.UserUnconfirmed(
        id=uuid.uuid4(),
        email=user_data.email,
        password_hash=password_hash,
        activation_token=activation_token,
        created_on=datetime.now(UTC),
        expire_on=datetime.now(UTC)
        + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS),
    )

    await cruds_users.create_unconfirmed_user(user_unconfirmed=user_unconfirmed, db=db)

    # After adding the unconfirmed user to the database, we got an activation token that need to be send by email,
    # in order to make sure the email address is valid

    if settings.SMTP_ACTIVE:
        activation_content = templates.get_template("activation_mail.html").render()
        background_tasks.add_task(
            send_email,
            recipient=user_data.email,
            subject="MyECL - confirm your email",
            content=activation_content,
            settings=settings,
        )
        rttrail_security_logger.info(
            f"Create_user: Creating an unconfirmed account for {user_data.email} ({request_id})",
        )
    else:
        rttrail_security_logger.info(
            f"Create_user: Creating an unconfirmed account for {user_data.email} ({request_id})",
        )


@router.get(
    "/users/{user_id}",
    response_model=schemas_users.User,
    status_code=200,
)
async def read_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: models_users.User = Depends(is_user(AccountType.admin)),
):
    """
    Return `User` representation of user with id `user_id`

    **The user must be authenticated to use this endpoint**
    """

    db_user = await cruds_users.get_user_by_id(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch(
    "/users/{user_id}",
    status_code=204,
)
async def update_user(
    user_id: uuid.UUID,
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


@router.get(
    "/users/{user_id}/profile-picture",
    response_class=FileResponse,
    status_code=200,
)
async def read_user_profile_picture(
    user_id: uuid.UUID,
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

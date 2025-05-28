import logging

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import cruds_users, models_users
from app.dependencies import (
    get_db,
    get_request_id,
    is_user,
)
from app.types import standard_responses
from app.types.content_type import ContentType
from app.types.module import CoreModule
from app.utils.tools import (
    get_file_from_data,
    save_file_as_data,
)
from app.core.users import schemas_users

from sqlalchemy.exc import IntegrityError


router = APIRouter(tags=["Me"])

core_module = CoreModule(
    tag="Me",
    router=router,
)

rttrail_error_logger = logging.getLogger("rttrail.error")
rttrail_security_logger = logging.getLogger("rttrail.security")

templates = Jinja2Templates(directory="assets/templates")


@router.get(
    "/users/me",
    response_model=schemas_users.User,
    status_code=200,
)
async def read_current_user(
    user: models_users.User = Depends(is_user()),
):
    """
    Return `User` representation of current user

    **The user must be authenticated to use this endpoint**
    """

    return user


@router.post(
    "/users/me/ask-deletion",
    status_code=204,
)
async def ask_user_deletion(
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


@router.post(
    "users/me/profile-picture",
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
    "users/me/profile-picture",
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

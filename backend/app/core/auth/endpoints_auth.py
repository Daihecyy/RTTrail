import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import schemas_auth
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

router = APIRouter(tags=["Auth"])

core_module = CoreModule(
    root="auth",
    tag="Auth",
    router=router,
)

templates = Jinja2Templates(directory="assets/templates")

# We could maybe use hyperion.security
rttrail_access_logger = logging.getLogger("rttrail.access")
rttrail_security_logger = logging.getLogger("rttrail.security")


@router.post(
    "/auth/simple_token",
    response_model=schemas_auth.AccessToken,
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
    data = schemas_auth.TokenData(sub=user.id, scopes=ScopeType.auth)
    access_token = create_access_token(settings=settings, data=data)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/test-token", response_model=schemas_users.User)
def test_token(current_user: models_users.User = Depends(is_user)):
    """
    Test access token
    """
    return current_user

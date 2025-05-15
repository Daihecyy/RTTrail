"""
Various FastAPI [dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

They are used in endpoints function signatures. For example:
```python
async def get_users(db: AsyncSession = Depends(get_db)):
```
"""

import logging
from collections.abc import AsyncGenerator, Callable, Coroutine
from functools import lru_cache
from typing import Any, cast

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.auth import schemas_auth
from app.core.users.type_users import AccountType
from app.core.users import models_users
from app.core.utils import security
from app.core.utils.config import Settings, construct_prod_settings
from app.types.scopes_type import ScopeType
from app.utils.auth import auth_utils

# We could maybe use hyperion.security
rttrail_access_logger = logging.getLogger("rttrail.access")
rttrail_error_logger = logging.getLogger("rttrail.error")

engine: AsyncEngine | None = (
    None  # Create a global variable for the database engine, so that it can be instancied in the startup event
)
SessionLocal: Callable[[], AsyncSession] | None = (
    None  # Create a global variable for the database session, so that it can be instancied in the startup event
)


async def get_request_id(request: Request) -> str:
    """
    The request identifier is a unique UUID which is used to associate logs saved during the same request
    """
    # `request_id` is a string injected in the state by our middleware
    # We force Mypy to consider it as a str instead of Any
    request_id = cast(str, request.state.request_id)

    return request_id


def init_and_get_db_engine(settings: Settings) -> AsyncEngine:
    """
    Return the (asynchronous) database engine, if the engine doesn't exit yet it will create one based on the settings
    """
    global engine
    global SessionLocal
    if settings.SQLITE_DB:
        SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///./{settings.SQLITE_DB}"
    else:
        SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

    if engine is None:
        engine = create_async_engine(
            SQLALCHEMY_DATABASE_URL,
            echo=settings.DATABASE_DEBUG,
        )
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Return a database session
    """
    if SessionLocal is None:
        rttrail_error_logger.error("Database engine is not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database engine is not initialized",
        )
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


async def get_unsafe_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Return a database session but don't close it automatically

    It should only be used for really specific cases where `get_db` will not work
    """
    if SessionLocal is None:
        rttrail_error_logger.error("Database engine is not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database engine is not initialized",
        )
    async with SessionLocal() as db:
        yield db


@lru_cache
def get_settings() -> Settings:
    """
    Return a settings object, based on `.env` dotenv
    """
    # `lru_cache()` decorator is here to prevent the class to be instantiated multiple times.
    # See https://fastapi.tiangolo.com/advanced/settings/#lru_cache-technical-details
    return construct_prod_settings()


def get_token_data(
    settings: Settings = Depends(get_settings),
    token: str = Depends(security.oauth2_scheme),
    request_id: str = Depends(get_request_id),
) -> schemas_auth.TokenData:
    """
    Dependency that returns the token payload data
    """
    return auth_utils.get_token_data(
        settings=settings,
        token=token,
        request_id=request_id,
    )


def get_user_from_token_with_scopes(
    scopes: list[list[ScopeType]],
) -> Callable[
    [AsyncSession, schemas_auth.TokenData],
    Coroutine[Any, Any, models_users.CoreUser],
]:
    """
    Generate a dependency which will:
     * check the request header contain a valid JWT token
     * make sure the token contain the given scopes
     * return the corresponding user `models_users.CoreUser` object

    This endpoint allows to require scopes other than the API scope. This should only be used by the auth endpoints.
    To restrict an endpoint from the API, use `is_user_in`.
    """

    async def get_current_user(
        db: AsyncSession = Depends(get_db),
        token_data: schemas_auth.TokenData = Depends(get_token_data),
    ) -> models_users.CoreUser:
        """
        Dependency that makes sure the token is valid, contains the expected scopes and returns the corresponding user.
        The expected scopes are passed as list of list of scopes, each list of scopes is an "AND" condition, and the list of list of scopes is an "OR" condition.
        """

        return await auth_utils.get_user_from_token_with_scopes(
            scopes=scopes,
            db=db,
            token_data=token_data,
        )

    return get_current_user


def is_user(
    account_type: AccountType | None = None,
) -> Callable[[models_users.CoreUser], models_users.CoreUser]:
    """
    A dependency that will:
        * check if the request header contains a valid API JWT token (a token that can be used to call endpoints from the API)
        * make sure the user making the request exists
        * verify the user has at least the right account type
    """
    account_type = account_type or AccountType.user

    def is_user(
        user: models_users.CoreUser = Depends(
            get_user_from_token_with_scopes([[ScopeType.API]]),
        ),
    ) -> models_users.CoreUser:
        if user.account_type == AccountType.admin:
            return user
        if account_type == AccountType.admin:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized, user does not have admin permissions",
            )

        if user.account_type == AccountType.moderator:
            return user
        if account_type == AccountType.moderator:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized, user does not have moderator permissions",
            )

        # else : user exists
        return user

    return is_user

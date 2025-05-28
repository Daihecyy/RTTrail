import logging

import jwt
from fastapi import HTTPException, status
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.login import schemas_login
from app.core.users import cruds_users, models_users
from app.core.utils import security
from app.core.utils.config import Settings
from app.types.scopes_type import ScopeType

rttrail_access_logger = logging.getLogger("rttrail.access")


def get_token_data(
    settings: Settings,
    token: str,
    request_id: str,
) -> schemas_login.TokenData:
    """
    Dependency that returns the token payload data
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.jwt_algorithm],
        )
        token_data = schemas_login.TokenData(**payload)
        rttrail_access_logger.info(
            f"Get_token_data: Decoded a token for user {token_data.sub} ({request_id})",
        )
    except ExpiredSignatureError:
        rttrail_access_logger.exception(
            f"Get_token_data: Token has expired ({request_id})",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token has expired",
        ) from None
    except DecodeError:
        rttrail_access_logger.exception(
            f"Get_token_data: Failed to decode a token ({request_id})",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None
    except (InvalidTokenError, ValidationError):
        rttrail_access_logger.exception(
            f"Get_token_data: Failed to decode a token ({request_id})",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None

    return token_data


async def get_user_from_token_with_scopes(
    scopes: list[list[ScopeType]],
    db: AsyncSession,
    token_data: schemas_login.TokenData,
) -> models_users.User:
    """
    Dependency that makes sure the token is valid, contains the expected scopes and returns the corresponding user.
    The expected scopes are passed as list of list of scopes, each list of scopes is an "AND" condition, and the list of list of scopes is an "OR" condition.
    """

    access_granted = False
    if scopes == []:
        access_granted = True
    else:
        for scope_set in scopes:
            # `token_data.scopes` contain a " " separated list of scopes
            # `scope_set` is a list of scopes that must be present in the token
            # If one of the scope set is present in the token, the access is granted

            scope_set_present = True
            for scope in scope_set:
                scope_set_present = scope_set_present and (
                    scope in token_data.scopes.split(" ")
                )
            access_granted = access_granted or scope_set_present

    if not access_granted:
        raise HTTPException(
            status_code=403,
            detail=f"Unauthorized, token does not contain at least one of the following scope_set {[[scope.value for scope in scope_set] for scope_set in scopes]}",
        )
    user_id = token_data.sub

    user = await cruds_users.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

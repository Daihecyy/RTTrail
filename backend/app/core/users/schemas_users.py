from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.utils import validators
from app.utils.examples import examples_users

from app.core.users.type_users import AccountType


class UserBase(BaseModel):
    """Base schema for user's model"""

    name: str

    _normalize_name = field_validator("name")(validators.trailing_spaces_remover)


class UserSimple(UserBase):
    """Simplified schema for user's model, used when getting all users"""

    id: UUID
    account_type: AccountType
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class User(UserSimple):
    """Schema for user's model similar to user table in database"""

    email: str
    created_on: datetime | None = None


class UserUpdate(BaseModel):
    """Schema for user update"""

    name: str | None = None

    _normalize_name = field_validator("name")(validators.trailing_spaces_remover)
    model_config = ConfigDict(json_schema_extra=examples_users.example_UserUpdate)


class UserUpdateAdmin(BaseModel):
    email: str | None = None
    account_type: AccountType | None = None
    name: str | None = None
    is_active: bool | None = None

    _normalize_name = field_validator("name")(validators.trailing_spaces_remover)
    model_config = ConfigDict(json_schema_extra=examples_users.example_UserUpdate)


class UserRegister(BaseModel):
    """
    The schema is used to send an account creation request.
    """

    email: str
    password: str
    name: str
    # Email normalization, this will modify the email variable
    # https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
    _normalize_email = field_validator("email")(validators.email_normalizer)
    _normalize_password = field_validator("password")(validators.password_validator)
    _normalize_name = field_validator("name")(validators.trailing_spaces_remover)
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=examples_users.example_CoreUserCreateRequest,
    )


class UserActivate(UserBase):
    activation_token: str
    # Password validator
    # https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=examples_users.example_CoreUserActivateRequest,
    )


class UserRecoverRequest(BaseModel):
    email: str
    user_id: UUID
    reset_token: str
    created_on: datetime
    expire_on: datetime

    _normalize_email = field_validator("email")(validators.email_normalizer)
    model_config = ConfigDict(from_attributes=True)


# Importing here to avoid circular imports

UserSimple.model_rebuild()

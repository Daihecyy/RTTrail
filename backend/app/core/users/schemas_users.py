from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.utils import validators
from app.utils.examples import examples_core

from app.core.users.type_users import AccountType


class UserBase(BaseModel):
    """Base schema for user's model"""

    name: str

    _normalize_name = field_validator("name")(validators.trailing_spaces_remover)


class UserSimple(UserBase):
    """Simplified schema for user's model, used when getting all users"""

    id: str
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
    model_config = ConfigDict(json_schema_extra=examples_core.example_CoreUserUpdate)


class UserUpdateAdmin(BaseModel):
    email: str | None = None
    account_type: AccountType | None = None
    name: str | None = None
    is_active: bool | None = None

    _normalize_name = field_validator("name")(validators.trailing_spaces_remover)
    model_config = ConfigDict(json_schema_extra=examples_core.example_CoreUserUpdate)


class UserCreateRequest(BaseModel):
    """
    The schema is used to send an account creation request.
    """

    email: str
    # Email normalization, this will modify the email variable
    # https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
    _normalize_email = field_validator("email")(validators.email_normalizer)
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=examples_core.example_CoreUserCreateRequest,
    )


class UserActivateRequest(UserBase):
    activation_token: str
    password: str
    # Password validator
    # https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
    _normalize_password = field_validator("password")(validators.password_validator)
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=examples_core.example_CoreUserActivateRequest,
    )


class UserRecoverRequest(BaseModel):
    email: str
    user_id: str
    reset_token: str
    created_on: datetime
    expire_on: datetime

    _normalize_email = field_validator("email")(validators.email_normalizer)
    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    email: str
    old_password: str
    new_password: str

    # Password validator
    # https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
    _normalize_password = field_validator("new_password")(validators.password_validator)


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str

    # Password validator
    # https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
    _normalize_password = field_validator("new_password")(validators.password_validator)


class MailMigrationRequest(BaseModel):
    new_email: str


# Importing here to avoid circular imports

UserSimple.model_rebuild()

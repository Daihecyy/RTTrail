"""Common schemas file for endpoint /users et /groups because it would cause circular import"""

from pydantic import BaseModel, ConfigDict

from app.core.users.type_users import AccountType


class CoreInformation(BaseModel):
    """Information about RTTrail"""

    ready: bool
    version: str


class ModuleVisibility(BaseModel):
    root: str
    allowed_account_types: list[AccountType]
    model_config = ConfigDict(from_attributes=True)


class ModuleVisibilityCreate(BaseModel):
    root: str
    allowed_account_type: AccountType | None = None
    model_config = ConfigDict(from_attributes=True)

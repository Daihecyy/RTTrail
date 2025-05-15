"""Common schemas file for endpoint /users et /groups because it would cause circular import"""

from pydantic import BaseModel


class CoreInformation(BaseModel):
    """Information about RTTrail"""

    ready: bool
    version: str

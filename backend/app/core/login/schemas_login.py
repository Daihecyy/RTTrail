"""Schemas file for endpoint /auth"""

from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, field_validator

from app.utils import validators


class ChangePassword(BaseModel):
    email: str
    old_password: str
    new_password: str

    # Password validator
    # https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
    _normalize_password = field_validator("new_password")(validators.password_validator)


class ResetPassword(BaseModel):
    reset_token: str
    new_password: str

    # Password validator
    # https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
    _normalize_password = field_validator("new_password")(validators.password_validator)


class MailMigration(BaseModel):
    new_email: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str  # Subject: the user id
    iss: str | None = None
    aud: str | None = None
    cid: str | None = None  # The client_id of the service which receives the token
    iat: datetime | None = None
    nonce: str | None = None
    scopes: str = ""
    # exp and iat elements are added by the token generation function


class TokenReq(BaseModel):
    refresh_token: str | None = None
    grant_type: str
    code: str | None = None
    redirect_uri: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    # PKCE parameters
    code_verifier: str | None = None

    @classmethod
    def as_form(
        cls,
        refresh_token: str | None = Form(None),
        grant_type: str = Form(...),
        code: str | None = Form(None),
        redirect_uri: str | None = Form(None),
        client_id: str | None = Form(None),
        client_secret: str | None = Form(None),
        # PKCE parameters
        code_verifier: str | None = Form(None),
    ):
        return cls(
            refresh_token=refresh_token,
            grant_type=grant_type,
            code=code,
            redirect_uri=redirect_uri,
            client_id=client_id,
            client_secret=client_secret,
            code_verifier=code_verifier,
        )

    class config:
        schema_extra = {
            "example": {
                "refresh_token": "Yi6wBcMVoUe-dYJ-ttd6dT8ZuKcUsJVnc4MaUxoLeXU",
                "grant_type": "refresh_token",
                "client_id": "5507cc3a-fd29-11ec-b939-0242ac120002",
            },
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    scope: str = ""
    refresh_token: str
    id_token: str | None = None


class IntrospectTokenReq(BaseModel):
    # https://datatracker.ietf.org/doc/html/rfc7662
    token: str
    token_type_hint: str | None = None
    client_id: str | None = None
    client_secret: str | None = None

    @classmethod
    def as_form(
        cls,
        token: str = Form(...),
        token_type_hint: str | None = Form(None),
        client_id: str | None = Form(None),
        client_secret: str | None = Form(None),
    ):
        return cls(
            token=token,
            token_type_hint=token_type_hint,
            client_id=client_id,
            client_secret=client_secret,
        )


class IntrospectTokenResponse(BaseModel):
    active: bool

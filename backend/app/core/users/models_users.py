from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.users.type_users import AccountType
from app.types.sqlalchemy import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    is_active: Mapped[bool]
    account_type: Mapped[AccountType]
    name: Mapped[str]
    created_on: Mapped[datetime | None]


class UserUnconfirmed(Base):
    __tablename__ = "user_unconfirmed"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
    )
    # The email column should not be unique.
    # Someone can indeed create more than one user creation request,
    # for example after losing the previously received confirmation email.
    # For each user creation request, a row will be added in this table with a new token
    email: Mapped[str]
    password_hash: Mapped[str]
    activation_token: Mapped[str]
    created_on: Mapped[datetime]
    expire_on: Mapped[datetime]


class UserRecoverRequest(Base):
    __tablename__ = "user_recover_request"

    # The email column should not be unique.
    # Someone can indeed create more than one password reset request,
    email: Mapped[str]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    reset_token: Mapped[str] = mapped_column(primary_key=True)
    created_on: Mapped[datetime]
    expire_on: Mapped[datetime]


class UserEmailMigrationCode(Base):
    __tablename__ = "user_email_migration_code"

    new_email: Mapped[str]
    old_email: Mapped[str]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)

    confirmation_token: Mapped[str] = mapped_column(
        String,
        nullable=False,
        primary_key=True,
    )

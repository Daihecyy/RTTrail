from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.users.type_users import AccountType
from app.types.sqlalchemy import Base


class CoreUser(Base):
    __tablename__ = "core_user"

    id: Mapped[str] = mapped_column(
        primary_key=True,
        index=True,
    )  # Use UUID later
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    account_type: Mapped[AccountType]
    name: Mapped[str]
    created_on: Mapped[datetime | None]


class CoreUserUnconfirmed(Base):
    __tablename__ = "core_user_unconfirmed"

    id: Mapped[str] = mapped_column(primary_key=True)
    # The email column should not be unique.
    # Someone can indeed create more than one user creation request,
    # for example after losing the previously received confirmation email.
    # For each user creation request, a row will be added in this table with a new token
    email: Mapped[str]
    activation_token: Mapped[str]
    created_on: Mapped[datetime]
    expire_on: Mapped[datetime]


class CoreUserRecoverRequest(Base):
    __tablename__ = "core_user_recover_request"

    # The email column should not be unique.
    # Someone can indeed create more than one password reset request,
    email: Mapped[str]
    user_id: Mapped[str]
    reset_token: Mapped[str] = mapped_column(primary_key=True)
    created_on: Mapped[datetime]
    expire_on: Mapped[datetime]


class CoreUserEmailMigrationCode(Base):
    __tablename__ = "core_user_email_migration_code"

    user_id: Mapped[str] = mapped_column(ForeignKey("core_user.id"), primary_key=True)
    new_email: Mapped[str]
    old_email: Mapped[str]

    confirmation_token: Mapped[str] = mapped_column(
        String,
        nullable=False,
        primary_key=True,
    )

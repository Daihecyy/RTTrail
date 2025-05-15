"""File defining the functions called by the endpoints, making queries to the table using the models"""

from collections.abc import Sequence

from sqlalchemy import and_, delete, not_, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users.type_users import AccountType
from app.core.users import models_users, schemas_users


async def count_users(db: AsyncSession) -> int:
    """Return the number of users in the database"""

    result = await db.execute(select(models_users.CoreUser))
    return len(result.scalars().all())


async def get_users(
    db: AsyncSession,
    included_account_types: list[AccountType] | None = None,
    excluded_account_types: list[AccountType] | None = None,
) -> Sequence[models_users.CoreUser]:
    """
    Return all users from database.

    Parameters `excluded_account_types` and `excluded_groups` can be used to filter results.
    """
    included_account_types = included_account_types or None
    excluded_account_types = excluded_account_types or []

    included_account_type_condition = (
        or_(
            False,
            *[
                models_users.CoreUser.account_type == account_type
                for account_type in included_account_types
            ],
        )
        if included_account_types
        else and_(True)
    )
    excluded_account_type_condition = [
        not_(
            models_users.CoreUser.account_type == account_type,
        )
        for account_type in excluded_account_types
    ]

    result = await db.execute(
        select(models_users.CoreUser).where(
            and_(
                True,
                included_account_type_condition,
                *excluded_account_type_condition,
            ),
        ),
    )
    return result.scalars().all()


async def get_user_by_id(
    db: AsyncSession,
    user_id: str,
) -> models_users.CoreUser | None:
    """Return user with id from database as a dictionary"""

    result = await db.execute(
        select(models_users.CoreUser).where(models_users.CoreUser.id == user_id),
    )
    return result.scalars().first()


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> models_users.CoreUser | None:
    """Return user with id from database as a dictionary"""

    result = await db.execute(
        select(models_users.CoreUser).where(models_users.CoreUser.email == email),
    )
    return result.scalars().first()


async def update_user(
    db: AsyncSession,
    user_id: str,
    user_update: schemas_users.CoreUserUpdateAdmin | schemas_users.CoreUserUpdate,
):
    await db.execute(
        update(models_users.CoreUser)
        .where(models_users.CoreUser.id == user_id)
        .values(**user_update.model_dump(exclude_none=True)),
    )


async def create_unconfirmed_user(
    db: AsyncSession,
    user_unconfirmed: models_users.CoreUserUnconfirmed,
) -> models_users.CoreUserUnconfirmed:
    """
    Create a new user in the unconfirmed database
    """

    db.add(user_unconfirmed)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    else:
        return user_unconfirmed  # TODO Is this useful ?


async def get_unconfirmed_user_by_activation_token(
    db: AsyncSession,
    activation_token: str,
) -> models_users.CoreUserUnconfirmed | None:
    result = await db.execute(
        select(models_users.CoreUserUnconfirmed).where(
            models_users.CoreUserUnconfirmed.activation_token == activation_token,
        ),
    )
    return result.scalars().first()


async def delete_unconfirmed_user_by_email(db: AsyncSession, email: str):
    """Delete a user from database by id"""

    await db.execute(
        delete(models_users.CoreUserUnconfirmed).where(
            models_users.CoreUserUnconfirmed.email == email,
        ),
    )
    await db.commit()


async def create_user(
    db: AsyncSession,
    user: models_users.CoreUser,
) -> models_users.CoreUser:
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    else:
        return user


async def delete_user(db: AsyncSession, user_id: str):
    """Delete a user from database by id"""

    await db.execute(
        delete(models_users.CoreUser).where(models_users.CoreUser.id == user_id),
    )
    await db.commit()


async def create_user_recover_request(
    db: AsyncSession,
    recover_request: models_users.CoreUserRecoverRequest,
) -> models_users.CoreUserRecoverRequest:
    db.add(recover_request)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    else:
        return recover_request


async def get_recover_request_by_reset_token(
    db: AsyncSession,
    reset_token: str,
) -> models_users.CoreUserRecoverRequest | None:
    result = await db.execute(
        select(models_users.CoreUserRecoverRequest).where(
            models_users.CoreUserRecoverRequest.reset_token == reset_token,
        ),
    )
    return result.scalars().first()


async def create_email_migration_code(
    migration_object: models_users.CoreUserEmailMigrationCode,
    db: AsyncSession,
) -> models_users.CoreUserEmailMigrationCode:
    db.add(migration_object)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    else:
        return migration_object


async def get_email_migration_code_by_token(
    confirmation_token: str,
    db: AsyncSession,
) -> models_users.CoreUserEmailMigrationCode | None:
    result = await db.execute(
        select(models_users.CoreUserEmailMigrationCode).where(
            models_users.CoreUserEmailMigrationCode.confirmation_token
            == confirmation_token,
        ),
    )
    return result.scalars().first()


async def delete_email_migration_code_by_token(
    confirmation_token: str,
    db: AsyncSession,
):
    await db.execute(
        delete(models_users.CoreUserEmailMigrationCode).where(
            models_users.CoreUserEmailMigrationCode.confirmation_token
            == confirmation_token,
        ),
    )
    await db.commit()


async def delete_recover_request_by_email(db: AsyncSession, email: str):
    """Delete a user from database by id"""

    await db.execute(
        delete(models_users.CoreUserRecoverRequest).where(
            models_users.CoreUserRecoverRequest.email == email,
        ),
    )
    await db.commit()


async def update_user_password_by_id(
    db: AsyncSession,
    user_id: str,
    new_password_hash: str,
):
    await db.execute(
        update(models_users.CoreUser)
        .where(models_users.CoreUser.id == user_id)
        .values(password_hash=new_password_hash),
    )
    await db.commit()

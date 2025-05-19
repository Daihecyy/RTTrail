from collections.abc import Sequence
from uuid import UUID
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.poi import models_poi
from backend.app.modules.poi.types_poi import VoteValue


async def create_poi(db: AsyncSession, poi: models_poi.POI) -> models_poi.POI:
    """Create a POI in db"""
    db.add(poi)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    else:
        return poi


async def get_poi_by_id(db: AsyncSession, poi_id: UUID) -> models_poi.POI | None:
    """Return a POI from its id"""
    poi = await db.execute(
        select(models_poi.POI).where(
            models_poi.POI.id == poi_id,
        ),
    )
    return poi.unique().scalars().first()


async def get_pois_in_box(
    db: AsyncSession, box_definition: str
) -> Sequence[models_poi.POI]:
    """Return POIs inside the box"""
    pois = await db.execute(select(models_poi.POI).filter(func.st_intersects))
    return pois.scalars().all()


async def update_poi_by_id(
    db: AsyncSession,
    poi_id: UUID,
    new_poi: schemas_poi.POIEdit,
):
    """Update a POI in db"""
    await db.execute(
        update(models_poi.POI)
        .where(
            models_poi.POI.id == poi_id,
        )
        .values(**new_poi.model_dump(exclude_none=True)),
    )


async def delete_poi_by_id(
    db: AsyncSession,
    poi_id: UUID,
):
    """Delete a POI in db"""
    await db.execute(
        delete(models_poi.POI).where(models_poi.POI.id == poi_id),
    )


async def create_vote(db: AsyncSession, vote: models_poi.Vote) -> models_poi.Vote:
    """Add a vote in db"""
    db.add(vote)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    else:
        return vote


async def get_vote_by_poi_id_and_user_id(
    db: AsyncSession, poi_id: UUID, user_id: UUID
) -> models_poi.Vote | None:
    """Return a vote from the POI's and the user's id"""
    vote = await db.execute(
        select(models_poi.Vote).where(
            models_poi.Vote.user_id == user_id,
            models_poi.Vote.poi_id == poi_id,
        ),
    )
    return vote.unique().scalars().first()


async def update_vote_value_by_poi_id_and_user_id(
    db: AsyncSession, poi_id: UUID, user_id: UUID, new_vote_value: VoteValue
):
    """Update the vote value in db based on the POI's and the user's id"""
    await db.execute(
        update(models_poi.Vote)
        .where(
            models_poi.Vote.user_id == user_id,
            models_poi.Vote.poi_id == poi_id,
        )
        .values(vote_value=new_vote_value)
    )


async def delete_vote_by_poi_id_and_user_id(
    db: AsyncSession,
    poi_id: UUID,
    user_id: UUID,
):
    """Delete a vote in db based on the POI's and the user's id"""
    await db.execute(
        delete(models_poi.Vote).where(
            models_poi.Vote.user_id == user_id,
            models_poi.Vote.poi_id == poi_id,
        )
    )

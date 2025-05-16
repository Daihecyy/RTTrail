from datetime import datetime
from uuid import UUID

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.users.models_users import User
from app.types.sqlalchemy import Base, PrimaryKey
from app.dependencies import SRID
from app.modules.poi.types_poi import VoteValue


class POI(Base):
    __tablename__ = "poi"

    id: Mapped[PrimaryKey]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship("User", init=False)
    creation_time: Mapped[datetime]
    title: Mapped[str]
    image_url: Mapped[str]
    mapped_geom: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=SRID)
    )
    description: Mapped[str]
    votes: Mapped[list["Vote"]] = relationship(
        "Vote",
        lazy="selectin",
        default_factory=list,
    )
    vote_score: Mapped[int]


class Vote(Base):
    __tablename__ = "vote"
    id: Mapped[PrimaryKey]
    poi_id: Mapped[UUID] = mapped_column(ForeignKey("poi.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship("User", init=False)
    vote_value: Mapped[VoteValue]

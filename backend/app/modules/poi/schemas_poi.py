import uuid
from datetime import datetime

from pydantic import BaseModel

from app.core.users.schemas_users import UserSimple
from app.modules.poi.types_poi import POIType


class POI(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    type: POIType
    vote_score: int

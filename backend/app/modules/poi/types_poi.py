from enum import Enum


class VoteValue(int, Enum):
    UP = 1
    DOWN = -1


class POIType(str, Enum):
    DANGER = "danger"
    DISREPEAR = "disrepear"
    DIFFICULTY = "difficulty"
    POV = "pov"
    OTHER = "other"

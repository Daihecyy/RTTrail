from enum import Enum


class VoteValue(int, Enum):
    UP = 1
    DOWN = -1

from enum import Enum


class AccountType(str, Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"

from fastapi import APIRouter

from app.core.users.type_users import AccountType


class CoreModule:
    def __init__(
        self,
        tag: str,
        router: APIRouter | None = None,
    ):
        """
        Initialize a new Module object.
        :param router: an optional custom APIRouter
        """
        self.router = router or APIRouter(tags=[tag])


class Module(CoreModule):
    def __init__(
        self,
        root: str,
        tag: str,
        default_allowed_account_types: list[AccountType] | None = None,
        router: APIRouter | None = None,
    ):
        """
        Initialize a new Module object.
        :param root: the root of the module, used by Titan
        :param default_allowed_account_types: list of account_types that should be able to see the module by default
        :param router: an optional custom APIRouter
        """
        self.root = root
        self.default_allowed_account_types = default_allowed_account_types
        self.router = router or APIRouter(tags=[tag])

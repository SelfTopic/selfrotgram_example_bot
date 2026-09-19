from selfrot import BaseRouter

from ..context import AppContext


class RootRouter(BaseRouter[AppContext]):
    # Пакеты роутеров: у каждого свой __init__.py с `router` и своим auto_connect.
    auto_connect = (".common", ".admin")


router = RootRouter

__all__ = ["RootRouter", "router"]

from selfrot import BaseRouter

from ...context import AppContext
from ...middlewares import AdminMiddleware


class AdminRouter(BaseRouter[AppContext]):
    # Внутренняя мидлварь: проверка админа на всё поддерево, а не на каждый апдейт.
    middlewares = (AdminMiddleware,)
    auto_connect = (".stats_router",)


router = AdminRouter

__all__ = ["AdminRouter", "router"]

from dataclasses import dataclass
from functools import cached_property

from selfrot import BaseContext, TEvent

from ..database import session_context
from .repositories import CooldownRepository, UserRepository
from .services import FactsService, UserService


@dataclass
class AppContext(BaseContext[TEvent]):
    """
    Зависимости хендлеров двух видов:

    - facts: без состояния и БД, один на приложение. Диспетчер кладёт его при
      создании контекста (Dispatcher.create_context).
    - user_service: работает с БД, поэтому строится лениво, при первом обращении, из
      сессии текущего апдейта (session_context). Работает только после
      DatabaseMiddleware. cached_property: за один апдейт сервис один и тот же.
    """

    facts: FactsService

    @cached_property
    def user_service(self) -> UserService:
        session = session_context.get()
        return UserService(UserRepository(session), CooldownRepository(session))

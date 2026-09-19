import logging
from typing import Any

from selfrot import BaseMiddleware

from ...database import session_factory
from ..context import AppContext
from ..repositories import CooldownRepository, UserRepository
from ..services import UserService

logger = logging.getLogger(__name__)


class SyncEntitiesMiddleware(BaseMiddleware[AppContext[Any]]):
    """
    Апсертит пользователя на каждый апдейт в СВОЕЙ, сразу коммитящейся сессии,
    а не в сессии хендлера: иначе UPSERT держал бы строку users залоченной, пока
    не закончится весь хендлер (у оригинала это была нарезка видео на десятки
    секунд, и следующее сообщение того же человека ждало на уровне Postgres).
    """

    async def pre_handle(self) -> bool:
        telegram_user = self.ctx.user
        if telegram_user is None:
            return True

        async with session_factory() as session:
            service = UserService(UserRepository(session), CooldownRepository(session))
            await service.upsert(telegram_user)
            await session.commit()

        return True

    async def post_handle(self, exc: BaseException | None = None) -> None:
        return None


__all__ = ["SyncEntitiesMiddleware"]

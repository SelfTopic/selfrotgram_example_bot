import logging
from contextvars import Token
from typing import Any

from selfrot import BaseContext, BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import session_context, session_factory

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware[BaseContext[Any]]):
    """
    Сессия БД на весь апдейт: открывается в pre_handle, коммитится или
    откатывается в post_handle. Диспетчер вызывает pre_handle, handle и
    post_handle в одной задаче, поэтому ContextVar виден хендлеру, а reset()
    в post_handle проходит.
    """

    session: AsyncSession
    _token: Token[AsyncSession]

    async def pre_handle(self) -> bool:
        self.session = session_factory()
        self._token = session_context.set(self.session)
        # Именно True: любое другое значение библиотека считает запретом.
        return True

    async def post_handle(self, exc: BaseException | None = None) -> None:
        try:
            if exc is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            session_context.reset(self._token)
            await self.session.close()


__all__ = ["DatabaseMiddleware"]

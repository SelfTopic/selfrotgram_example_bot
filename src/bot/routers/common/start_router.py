import logging
from html import escape

from selfrot import BaseRouter, MessageHandler
from selfrot.filter import Command, HasUser
from selfrot.types import UserMessage

from ...context import AppContext
from ...exceptions import UserError
from ...keyboards import menu_keyboard
from ...texts import HOME_TEXT

logger = logging.getLogger(__name__)


class Start(MessageHandler[AppContext[UserMessage]]):
    # /start без аргументов (в оригинале CommandStart(deep_link=False)) или /menu.
    # HasUser гарантирует отправителя, поэтому проверка `if not from_user` не нужна.
    query = (Command("start", args_count=0) | Command("menu")) & HasUser()

    async def handle(self) -> None:
        # Пользователя уже записал SyncEntitiesMiddleware.
        user = await self.ctx.user_service.get(self.ctx.message.user.id)
        if not user:
            raise UserError("Не получилось найти тебя в базе, попробуй ещё раз")

        logger.debug(f"User equal {user}")

        await self.ctx.answer_message(
            f"Привет, {escape(user.first_name)}! 👋\n\n{HOME_TEXT}",
            reply_markup=menu_keyboard(),
        )


class StartRouter(BaseRouter[AppContext]):
    handlers = (Start,)


# auto_connect ищет в модуле объект с именем `router`.
router = StartRouter

__all__ = ["StartRouter", "router"]

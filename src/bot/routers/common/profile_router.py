from selfrot import BaseRouter, MessageHandler
from selfrot.filter import Command, HasUser
from selfrot.types import TextMessage, UserMessage

from ...context import AppContext
from ...exceptions import UserError
from ...texts import profile_text, top_text
from ...services.user import BONUS_AMOUNT


class Me(MessageHandler[AppContext[UserMessage]]):
    query = Command("me") & HasUser()

    async def handle(self) -> None:
        user = await self.ctx.user_service.get(self.ctx.message.user.id)
        if not user:
            raise UserError("Тебя нет в базе, отправь /start")

        await self.ctx.reply_message(profile_text(user))


class Bonus(MessageHandler[AppContext[UserMessage]]):
    query = Command("bonus") & HasUser()

    async def handle(self) -> None:
        # Слишком рано: сервис бросает BonusCooldownError, его ловит Dispatcher.on_error.
        user = await self.ctx.user_service.claim_bonus(self.ctx.message.user.id)
        await self.ctx.reply_message(
            f"🎁 +{BONUS_AMOUNT}! Баланс: <b>{user.balance}</b>"
        )


class Top(MessageHandler[AppContext[TextMessage]]):
    query = Command("top")

    async def handle(self) -> None:
        await self.ctx.reply_message(top_text(await self.ctx.user_service.top()))


class ProfileRouter(BaseRouter[AppContext]):
    handlers = (Me, Bonus, Top)


router = ProfileRouter

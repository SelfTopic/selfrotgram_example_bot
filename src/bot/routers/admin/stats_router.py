from selfrot import BaseRouter, MessageHandler
from selfrot.filter import Command
from selfrot.types import TextMessage

from ...context import AppContext


class Stats(MessageHandler[AppContext[TextMessage]]):
    query = Command("stats")

    async def handle(self) -> None:
        total = await self.ctx.user_service.count()
        await self.ctx.answer_message(f"📊 Пользователей в базе: <b>{total}</b>")


class StatsRouter(BaseRouter[AppContext]):
    handlers = (Stats,)


router = StatsRouter

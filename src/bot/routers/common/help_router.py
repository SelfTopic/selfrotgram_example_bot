from selfrot import BaseRouter, MessageHandler
from selfrot.filter import Command
from selfrot.types import TextMessage

from ...context import AppContext
from ...texts import HELP_TEXT


class Help(MessageHandler[AppContext[TextMessage]]):
    query = Command("help")

    async def handle(self) -> None:
        await self.ctx.answer_message(HELP_TEXT)


class HelpRouter(BaseRouter[AppContext]):
    handlers = (Help,)


router = HelpRouter

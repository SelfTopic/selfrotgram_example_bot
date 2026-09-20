from html import escape

from selfrot import BaseRouter, MessageHandler
from selfrot.filter import HasUser, TextRegexp, TextStartswith
from selfrot.types import TextMessage, UserMessage

from ...context import AppContext


class Greeting(MessageHandler[AppContext[UserMessage]]):
    # (A | B) & C: текст начинается с одного из слов, и отправитель известен.
    query = (
        TextStartswith("привет", ignore_case=True)
        | TextStartswith("hello", ignore_case=True)
    ) & HasUser()

    async def handle(self) -> None:
        name = escape(self.ctx.message.user.first_name)
        await self.ctx.reply_message(f"Привет, {name}! 👋")


class QuickCalc(MessageHandler[AppContext[TextMessage]]):
    # «2+2», «10 / 4»: регулярка разбирает выражение, match() отдаёт совпадение.
    calc = TextRegexp(r"\s*(-?\d+)\s*([+\-*/])\s*(-?\d+)\s*", full=True)
    query = calc

    async def handle(self) -> None:
        left, op, right = self.calc.match(self.ctx).groups()
        a, b = int(left), int(right)
        if op == "/" and b == 0:
            await self.ctx.reply_message("На ноль делить нельзя 🙅")
            return

        result = {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b else 0}[op]
        await self.ctx.reply_message(f"{a} {op} {b} = <b>{result:g}</b>")


class TextRouter(BaseRouter[AppContext]):
    handlers = (Greeting, QuickCalc)


router = TextRouter

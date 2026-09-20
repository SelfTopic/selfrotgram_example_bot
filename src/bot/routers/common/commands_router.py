import random
from html import escape
from typing import Annotated, Literal

from pydantic import Field
from selfrot import BaseRouter, CommandArgs, MessageHandler, Rest
from selfrot.filter import Command
from selfrot.types import TextMessage

from ...context import AppContext


class Ping(MessageHandler[AppContext[TextMessage]]):
    # prefixes="/!": работает и /ping, и !ping.
    query = Command("ping", prefixes="/!")

    async def handle(self) -> None:
        await self.ctx.reply_message("pong 🏓")


# Аргументы команды как данные: форму описываем один раз, разбор, типы и проверку
# делает библиотека. Неверные аргументы бросают CommandArgsError, а подсказку для
# всех команд сразу отправляет Dispatcher.on_error (см. __main__.py).


class EchoArgs(CommandArgs):
    text: Rest  # весь остаток строки, с пробелами


class Echo(MessageHandler[AppContext[TextMessage]]):
    # Фильтр кладём в атрибут: в хендлере им же разбираем аргументы (parse).
    cmd = Command("echo", EchoArgs)
    query = cmd

    async def pre_handle(self) -> None:
        self.args = self.cmd.parse(self.ctx)  # EchoArgs; ошибка не дойдёт до handle

    async def handle(self) -> None:
        await self.ctx.reply_message(escape(self.args.text))


class CalcArgs(CommandArgs):
    one: int
    operator: Literal["+", "-", "*", "/"]  # только эти четыре
    two: int


class Calc(MessageHandler[AppContext[TextMessage]]):
    """/calc 2 + 3"""

    cmd = Command("calc", CalcArgs)
    query = cmd

    async def pre_handle(self) -> None:
        self.args = self.cmd.parse(self.ctx)

    async def handle(self) -> None:
        a = self.args  # one и two уже int, operator из Literal
        result: int | str
        match a.operator:
            case "+":
                result = a.one + a.two
            case "-":
                result = a.one - a.two
            case "*":
                result = a.one * a.two
            case "/":
                result = f"{a.one / a.two:g}" if a.two else "на ноль делить нельзя"

        await self.ctx.reply_message(f"{a.one} {a.operator} {a.two} = <b>{result}</b>")


class RollArgs(CommandArgs):
    # Значение по умолчанию: аргумент можно не писать. Ограничения pydantic работают.
    sides: Annotated[int, Field(ge=2, le=1000)] = 6


class Roll(MessageHandler[AppContext[TextMessage]]):
    """/roll или /roll 20"""

    cmd = Command("roll", RollArgs)
    query = cmd

    async def pre_handle(self) -> None:
        self.args = self.cmd.parse(self.ctx)

    async def handle(self) -> None:
        await self.ctx.reply_message(
            f"🎲 d{self.args.sides}: <b>{random.randint(1, self.args.sides)}</b>"
        )


class Say(MessageHandler[AppContext[TextMessage]]):
    # Имя из двух слов и без префикса: «Бот скажи привет». Без модели аргументов
    # parse отдаёт сырой разбор (rest, args).
    cmd = Command("бот скажи", prefixes="", ignore_case=True)
    query = cmd

    async def handle(self) -> None:
        rest = self.cmd.parse(self.ctx).rest
        await self.ctx.reply_message(escape(rest) if rest else "Что сказать?")


class CommandsRouter(BaseRouter[AppContext]):
    handlers = (Ping, Echo, Calc, Roll, Say)


router = CommandsRouter

import random
from html import escape

from selfrot import BaseRouter, MessageHandler
from selfrot.filter import Command
from selfrot.types import TextMessage

from ...context import AppContext


class Ping(MessageHandler[AppContext[TextMessage]]):
    # prefixes="/!": работает и /ping, и !ping.
    query = Command("ping", prefixes="/!")

    async def handle(self) -> None:
        await self.ctx.reply_message("pong 🏓")


class Echo(MessageHandler[AppContext[TextMessage]]):
    # Фильтр кладём в атрибут: в хендлере им же разбираем аргументы (parse).
    cmd = Command("echo")
    query = cmd

    async def handle(self) -> None:
        rest = self.cmd.parse(self.ctx).rest  # всё после команды одной строкой
        if not rest:
            await self.ctx.reply_message("Использование: <code>/echo текст</code>")
            return

        await self.ctx.reply_message(escape(rest))


class Sum(MessageHandler[AppContext[TextMessage]]):
    # args_count=2: /sum с другим числом аргументов этому хендлеру не подходит.
    cmd = Command("sum", args_count=2)
    query = cmd

    async def pre_handle(self) -> None:
        # Разбор и проверка до handle. Исключение отсюда попадает в on_error.
        self.a, self.b = (int(arg) for arg in self.cmd.parse(self.ctx).args)

    async def handle(self) -> None:
        await self.ctx.reply_message(f"{self.a} + {self.b} = <b>{self.a + self.b}</b>")

    async def on_error(self, exc: Exception) -> None:
        if isinstance(exc, ValueError):
            await self.ctx.reply_message("Нужны два целых числа: <code>/sum 2 3</code>")
            return
        raise exc  # чужое отдаём выше, в Dispatcher.on_error


class SumUsage(MessageHandler[AppContext[TextMessage]]):
    # Стоит после Sum: сюда доходит /sum с любым другим числом аргументов.
    query = Command("sum")

    async def handle(self) -> None:
        await self.ctx.reply_message("Использование: <code>/sum 2 3</code>")


class Roll(MessageHandler[AppContext[TextMessage]]):
    # Фильтры складываются через |; вторая команда без префикса и без учёта регистра.
    query = Command("roll") | Command("кубик", prefixes="", ignore_case=True)

    async def handle(self) -> None:
        await self.ctx.reply_message(f"🎲 Выпало: <b>{random.randint(1, 6)}</b>")


class Say(MessageHandler[AppContext[TextMessage]]):
    # Имя из двух слов и без префикса: «Бот скажи привет».
    cmd = Command("бот скажи", prefixes="", ignore_case=True)
    query = cmd

    async def handle(self) -> None:
        rest = self.cmd.parse(self.ctx).rest
        await self.ctx.reply_message(escape(rest) if rest else "Что сказать?")


class CommandsRouter(BaseRouter[AppContext]):
    handlers = (Ping, Echo, Sum, SumUsage, Roll, Say)


router = CommandsRouter

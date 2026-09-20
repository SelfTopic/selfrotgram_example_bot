import asyncio
import logging
from html import escape
from typing import Annotated

from pydantic import Field
from selfrot import BaseRouter, CommandArgs, MessageHandler, Rest
from selfrot.filter import Command
from selfrot.types import TextMessage

from ....database import session_factory
from ...context import AppContext
from ...repositories import UserRepository

logger = logging.getLogger(__name__)

# Отложенные действия: сделать что-то ПОСЛЕ того, как хендлер закончил. Хендлер не
# ждёт: слот диспетчера и сессия БД освобождаются сразу. Таймеры живут в памяти и
# при перезапуске бота пропадают.

SECRET_TTL = 10  # секунд до самоуничтожения сообщения
REPORT_SECONDS = 3  # сколько «готовится отчёт»


class Secret(MessageHandler[AppContext[TextMessage]]):
    """/secret: код, который удалится сам."""

    query = Command("secret")

    async def handle(self) -> None:
        sent = await self.ctx.reply_message(f"Код: 1234 (удалю через {SECRET_TTL} с)")
        self.defer(sent.delete, delay=SECRET_TTL)  # записали, что делать потом


class RemindArgs(CommandArgs):
    seconds: Annotated[int, Field(ge=1, le=3600)]
    text: Rest


class Remind(MessageHandler[AppContext[TextMessage]]):
    """/remind 5 позвонить маме: напомнить через 5 секунд."""

    cmd = Command("remind", RemindArgs)
    query = cmd

    async def pre_handle(self) -> None:
        self.args = self.cmd.parse(self.ctx)

    async def handle(self) -> None:
        self.reminder = self.defer(self.remind, self.args.text, delay=self.args.seconds)
        await self.ctx.reply_message(f"Напомню через {self.args.seconds} с")

    async def remind(self, text: str) -> None:
        # Выполняется уже после закрытия хендлера. Есть self и self.ctx.
        await self.ctx.answer_message(f"⏰ Напоминание: {escape(text)}")


class Report(MessageHandler[AppContext[TextMessage]]):
    """/report: быстрая часть в handle, долгая в after_handle."""

    query = Command("report")

    async def handle(self) -> None:
        self.processing = await self.ctx.reply_message("⏳ Готовлю отчёт...")
        # handle закончился: слот освобождён, сессия БД закоммичена и закрыта

    async def after_handle(self) -> None:
        await asyncio.sleep(REPORT_SECONDS)  # тут мог бы ждать результат фоновой задачи
        # Сессии хендлера уже нет: для работы с БД нужна своя.
        async with session_factory() as session:
            total = await UserRepository(session).count()

        await self.processing.edit_text(f"✅ Отчёт готов: пользователей в базе <b>{total}</b>")

    async def on_error(self, exc: Exception) -> None:
        # Сюда попадают и ошибки из after_handle.
        logger.error("Report failed", exc_info=exc)
        await self.ctx.answer_message("❌ Не получилось подготовить отчёт")


class DeferredRouter(BaseRouter[AppContext]):
    handlers = (Secret, Remind, Report)


router = DeferredRouter

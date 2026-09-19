import logging
from html import escape

from selfrot import BaseRouter
from selfrot.filter import ChatMemberTransition, MemberJoined, MemberLeft
from selfrot.handlers import ChatMemberHandler, MyChatMemberHandler
from selfrot.types import ChatMemberUpdated

from ...context import AppContext

logger = logging.getLogger(__name__)


class Joined(ChatMemberHandler[AppContext[ChatMemberUpdated]]):
    # Раньше не был в чате, теперь в чате: вошёл, добавлен, одобрена заявка.
    # Нужно, чтобы бот был админом группы: иначе chat_member не приходят.
    query = MemberJoined()

    async def handle(self) -> None:
        member = self.ctx.chat_member.new_chat_member.user
        await self.ctx.answer_message(f"👋 Добро пожаловать, {escape(member.first_name)}!")


class Left(ChatMemberHandler[AppContext[ChatMemberUpdated]]):
    query = MemberLeft()

    async def handle(self) -> None:
        member = self.ctx.chat_member.old_chat_member.user
        await self.ctx.answer_message(f"😢 {escape(member.first_name)} покинул чат")


class BotAdded(MyChatMemberHandler[AppContext[ChatMemberUpdated]]):
    # my_chat_member: статус самого бота. Переход между конкретными статусами.
    query = ChatMemberTransition(
        before={"left", "kicked"}, after={"member", "administrator"}
    )

    async def handle(self) -> None:
        await self.ctx.answer_message(
            "Спасибо, что добавили! Сделайте меня админом, и я буду встречать новичков. /help"
        )


class BotBlocked(MyChatMemberHandler[AppContext[ChatMemberUpdated]]):
    # Пользователь заблокировал бота (или бота выгнали): отвечать некуда, только лог.
    query = ChatMemberTransition(after="kicked")

    async def handle(self) -> None:
        logger.info(f"Bot was blocked in chat {self.ctx.chat_id}")


class ChatMemberRouter(BaseRouter[AppContext]):
    handlers = (Joined, Left, BotAdded, BotBlocked)


router = ChatMemberRouter

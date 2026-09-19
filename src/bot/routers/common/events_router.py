from selfrot import BaseRouter, MessageHandler
from selfrot.filter import HasPhoto, HasText
from selfrot.handlers import EditedMessageHandler
from selfrot.types import PhotoMessage, TextMessage

from ...context import AppContext


class Photo(MessageHandler[AppContext[PhotoMessage]]):
    # HasPhoto гарантирует поле photo: ни `if message.photo`, ни cast не нужны.
    query = HasPhoto()

    async def handle(self) -> None:
        biggest = self.ctx.message.photo[-1]  # Telegram присылает размеры по возрастанию
        size = f", {biggest.file_size // 1024} КБ" if biggest.file_size else ""
        await self.ctx.reply_message(
            f"📷 Фото {biggest.width}×{biggest.height}{size}\n"
            f"file_id: <code>{biggest.file_id}</code>"
        )


class Edited(EditedMessageHandler[AppContext[TextMessage]]):
    # Другой вид апдейта (edited_message): диспетчер сам добавит его в allowed_updates.
    query = HasText()

    async def handle(self) -> None:
        await self.ctx.reply_message("✏️ Вижу, что ты отредактировал сообщение")


class EventsRouter(BaseRouter[AppContext]):
    handlers = (Photo, Edited)


router = EventsRouter

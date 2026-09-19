from typing import Any

from selfrot.exceptions import TelegramBadRequest


async def edit_or_ignore(ctx: Any, text: str, markup: Any = None) -> None:
    """Правит сообщение под кнопкой; «message is not modified» (нажали то же самое) не ошибка."""
    try:
        await ctx.edit_message_text(text, reply_markup=markup)
    except TelegramBadRequest as e:
        if "not modified" not in str(e):
            raise

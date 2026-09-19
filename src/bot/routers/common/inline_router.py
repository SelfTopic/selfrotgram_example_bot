import logging
from html import escape

from selfrot import BaseRouter
from selfrot.handlers import ChosenInlineResultHandler, InlineQueryHandler
from selfrot.types import (
    ChosenInlineResult,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from ...context import AppContext

logger = logging.getLogger(__name__)


def _article(id: str, title: str, text: str) -> InlineQueryResultArticle:
    # parse_mode подставит Bot.defaults, поэтому text приходит уже экранированным.
    return InlineQueryResultArticle(
        id=id,
        title=title,
        description=text[:60],
        input_message_content=InputTextMessageContent(message_text=text),
    )


class Inline(InlineQueryHandler[AppContext[InlineQuery]]):
    # Без query подходит любой inline-запрос: `@бот что-нибудь`.
    async def handle(self) -> None:
        text = self.ctx.inline_query.query.strip()

        results = [_article("fact", "💡 Случайный факт", self.ctx.facts.random())]
        if text:
            results += [
                _article("upper", "ВЕРХНИЙ РЕГИСТР", escape(text.upper())),
                _article("lower", "нижний регистр", escape(text.lower())),
                _article("reverse", "Наоборот", escape(text[::-1])),
                _article("bold", "Жирный", f"<b>{escape(text)}</b>"),
            ]

        # У объекта есть свои методы: id запроса подставляется сам.
        await self.ctx.inline_query.answer(results, cache_time=1, is_personal=True)


class Chosen(ChosenInlineResultHandler[AppContext[ChosenInlineResult]]):
    # Приходит, если в @BotFather включить /setinlinefeedback.
    async def handle(self) -> None:
        chosen = self.ctx.chosen_inline_result
        logger.info(f"Inline result {chosen.result_id!r} chosen by {chosen.user.id}")


class InlineRouter(BaseRouter[AppContext]):
    handlers = (Inline, Chosen)


router = InlineRouter

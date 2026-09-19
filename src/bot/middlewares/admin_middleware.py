from typing import Any

from selfrot import BaseMiddleware

from ...config import ADMIN_IDS
from ..context import AppContext


class AdminMiddleware(BaseMiddleware[AppContext[Any]]):
    """
    Пускает только ADMIN_IDS. Навешен на роутер, поэтому срабатывает только если
    в его поддереве нашёлся хендлер: остальные апдейты его не видят. Возврат False
    из pre_handle не пускает апдейт в хендлер (post_handle тогда не вызывается).
    """

    async def pre_handle(self) -> bool:
        user = self.ctx.user
        if user is not None and user.id in ADMIN_IDS:
            return True

        await self.ctx.answer_message("⛔ Только для админов.")
        return False

    async def post_handle(self, exc: BaseException | None = None) -> None:
        return None

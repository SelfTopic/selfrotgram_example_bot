from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.models import Cooldown
from ..utils import utcnow
from .base import dialect_insert


class CooldownRepository:
    session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def try_claim(self, telegram_id: int, kind: str, seconds: int) -> bool:
        """
        Занять кулдаун одним запросом: вставить строку или продлить, если старая
        уже истекла. True — действие можно делать; False — ещё рано. Проверка и
        запись в одном INSERT ... ON CONFLICT ... WHERE, поэтому два одновременных
        нажатия не пройдут оба.
        """
        now = utcnow()
        until = now + timedelta(seconds=seconds)
        stmt = (
            dialect_insert(self.session, Cooldown)
            .values(telegram_id=telegram_id, kind=kind, until=until)
            .on_conflict_do_update(
                index_elements=["telegram_id", "kind"],
                set_={"until": until},
                where=Cooldown.until <= now,
            )
            .returning(Cooldown.telegram_id)
        )
        return await self.session.scalar(stmt) is not None

    async def seconds_left(self, telegram_id: int, kind: str) -> int:
        until = await self.session.scalar(
            select(Cooldown.until).where(
                Cooldown.telegram_id == telegram_id, Cooldown.kind == kind
            )
        )
        if until is None:
            return 0
        return max(0, int((until - utcnow()).total_seconds()) + 1)

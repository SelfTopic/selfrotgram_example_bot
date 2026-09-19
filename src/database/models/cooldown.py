from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

from .base import Base


class Cooldown(Base):
    """Кулдаун действия `kind` у пользователя: до `until` его повторить нельзя."""

    __tablename__ = "cooldowns"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    kind: Mapped[str] = mapped_column(primary_key=True)
    until: Mapped[datetime] = mapped_column(nullable=False)

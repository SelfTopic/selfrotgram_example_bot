from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)

    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    username: Mapped[Optional[str]] = mapped_column(nullable=True, unique=True)

    balance: Mapped[int] = mapped_column(nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    @property
    def full_name(self) -> str:
        return self.first_name + " " + (self.last_name or "")

import logging
from typing import Optional, Sequence, Union

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.models import User
from .base import dialect_insert

logger = logging.getLogger(__name__)


class UserRepository:
    session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(
        self,
        telegram_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> User:
        # Атомарно, а не "прочитать, потом записать": два апдейта одного
        # пользователя одновременно не упрутся в unique.
        stmt = (
            dialect_insert(self.session, User)
            .values(
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
            )
            .on_conflict_do_update(
                index_elements=["telegram_id"],
                set_={
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                },
            )
            .returning(User)
        )

        user = await self.session.scalar(stmt)
        if user is None:
            raise RuntimeError(f"User ({telegram_id}) not found after UPSERT")

        await self.session.refresh(user)
        return user

    async def get(self, search_parameter: Union[str, int]) -> Optional[User]:
        column = User.telegram_id if isinstance(search_parameter, int) else User.username
        return await self.session.scalar(select(User).where(column == search_parameter))

    async def add_balance(self, telegram_id: int, amount: int) -> Optional[User]:
        """Атомарное `balance = balance + amount`, без чтения в Python."""
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(balance=User.balance + amount)
            .returning(User)
            .execution_options(synchronize_session=False)
        )
        user = await self.session.scalar(stmt)
        if user is not None:
            await self.session.refresh(user)
        return user

    async def try_debit(self, telegram_id: int, amount: int) -> Optional[User]:
        """
        Списать, только если хватает: проверка и списание одним UPDATE ... WHERE balance >= amount.
        None: не хватило (или пользователя нет), ничего не изменилось.
        """
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id, User.balance >= amount)
            .values(balance=User.balance - amount)
            .returning(User)
            .execution_options(synchronize_session=False)
        )
        user = await self.session.scalar(stmt)
        if user is not None:
            await self.session.refresh(user)
        return user

    async def top(self, limit: int) -> Sequence[User]:
        stmt = select(User).order_by(User.balance.desc(), User.id).limit(limit)
        return (await self.session.scalars(stmt)).all()

    async def count(self) -> int:
        return await self.session.scalar(select(func.count()).select_from(User)) or 0

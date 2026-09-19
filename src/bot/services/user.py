import logging
from typing import Optional, Sequence, Union

from selfrot.types import User as TelegramUser

from ...database.models import User
from ..exceptions import BonusCooldownError, UserError
from ..repositories import CooldownRepository, UserRepository

logger = logging.getLogger(__name__)

BONUS_AMOUNT = 10
BONUS_COOLDOWN = 60  # секунд


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        cooldown_repository: CooldownRepository,
    ) -> None:
        self.user_repository = user_repository
        self.cooldown_repository = cooldown_repository

    async def upsert(self, telegram_user: TelegramUser) -> Optional[User]:
        if telegram_user.is_bot:
            logger.debug("User is bot, skipping registration")
            return None

        return await self.user_repository.upsert(
            telegram_id=telegram_user.id,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            username=telegram_user.username,
        )

    async def get(self, find_by: Union[str, int]) -> Optional[User]:
        return await self.user_repository.get(search_parameter=find_by)

    async def claim_bonus(self, telegram_id: int) -> User:
        # Кулдаун и начисление в одной транзакции: упадёт начисление, откатится и кулдаун.
        if not await self.cooldown_repository.try_claim(
            telegram_id, "bonus", BONUS_COOLDOWN
        ):
            left = await self.cooldown_repository.seconds_left(telegram_id, "bonus")
            raise BonusCooldownError(left)

        user = await self.user_repository.add_balance(telegram_id, BONUS_AMOUNT)
        if user is None:
            raise UserError("Сначала отправь /start")
        return user

    async def top(self, limit: int = 5) -> Sequence[User]:
        return await self.user_repository.top(limit)

    async def count(self) -> int:
        return await self.user_repository.count()

import logging
import sys
from os import environ

from dotenv import load_dotenv
from selfrot import BaseDispatcher
from selfrot.middleware import LoggingMiddleware
from selfrot.types import Update

from ..database import engine
from ..database.models import Base
from .bot import DemoBot
from .context import AppContext
from .exceptions import UserError
from .middlewares import DatabaseMiddleware, SyncEntitiesMiddleware
from .services import FactsService

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class Dispatcher(BaseDispatcher[AppContext]):
    bot = DemoBot
    context = AppContext
    auto_connect = (".routers",)
    middlewares = (LoggingMiddleware, DatabaseMiddleware, SyncEntitiesMiddleware)

    def __init__(self, token: str | None = None) -> None:
        super().__init__(token)
        self.facts = FactsService()

    def create_context(self, update: Update) -> AppContext:
        return self.context(update, self.api, facts=self.facts)

    async def on_error(self, ctx: AppContext, exc: Exception) -> None:
        if not isinstance(exc, UserError):
            await super().on_error(ctx, exc)
            return

        await ctx.answer_message(str(exc))

    async def on_startup(self) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def on_shutdown(self) -> None:
        await engine.dispose()


def main() -> None:
    token = environ.get("BOT_TOKEN")
    if not token:
        logger.fatal("Bot token is not found (переменная BOT_TOKEN)")
        sys.exit(1)

    logger.info("Run polling")
    Dispatcher(token=token).start_polling()
    logger.info("Programm finished")


if __name__ == "__main__":
    main()

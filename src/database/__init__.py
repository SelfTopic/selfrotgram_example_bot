from contextvars import ContextVar
from os import environ

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

# Для теста SQLite, чтобы не поднимать Postgres; в проде вместо неё postgresql+psycopg.
url = environ.get("DATABASE_URL", "sqlite+aiosqlite:///./dev.db")

engine = create_async_engine(url=url, echo=False)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

# Сессия текущего апдейта: её кладёт DatabaseMiddleware, читают хендлеры и
# (позже) DI-контейнер. В оригинале жила в containers.py.
session_context: ContextVar[AsyncSession] = ContextVar("session_context")

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession


def dialect_insert(session: AsyncSession, model: type):
    """ON CONFLICT есть в обоих диалектах, но insert() у каждого свой: в проде Postgres, для теста SQLite."""
    if session.get_bind().dialect.name == "sqlite":
        return sqlite_insert(model)
    return pg_insert(model)

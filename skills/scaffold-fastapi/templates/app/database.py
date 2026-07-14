"""Async SQLAlchemy engine/session setup and the `get_db` FastAPI dependency."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def ping_database(session: AsyncSession) -> None:
    await session.execute(text("SELECT 1"))


async def get_db():
    async with async_session_maker() as db:
        try:
            yield db
        finally:
            await db.close()

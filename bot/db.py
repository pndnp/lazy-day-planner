from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

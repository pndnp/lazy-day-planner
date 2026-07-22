
from sqlalchemy import text

from bot.db import async_session_factory


async def apply_migrations() -> None:
    """Lightweight migrations for SQLite.

    Adds missing columns without data loss.
    """
    async with async_session_factory() as session:
        # Check whether users.settings_json exists (SQLite-specific)
        result = await session.execute(
            text("PRAGMA table_info(users)")
        )
        columns = {row[1] for row in result.all()}

        if "settings_json" not in columns:
            await session.execute(
                text('ALTER TABLE users ADD COLUMN settings_json TEXT DEFAULT "{}"')
            )
            await session.commit()

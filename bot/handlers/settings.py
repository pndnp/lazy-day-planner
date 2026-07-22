from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select

from bot.db import async_session_factory
from bot.models import User

settings_router = Router()


@settings_router.message(Command("skipempty"))
async def cmd_skipempty(message: types.Message) -> None:
    """Toggle skipping empty daily summaries."""
    telegram_id = message.from_user.id

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=telegram_id)
            session.add(user)

        new_val: bool = user.toggle_setting("skip_empty", default=False)
        await session.commit()

    if new_val:
        text = (
            "Пропуск пустых рассылок: <b>включено</b>.\n\n"
            "Теперь, если на сегодня нет событий, "
            "утреннее сообщение не придёт."
        )
    else:
        text = (
            "Пропуск пустых рассылок: <b>отключено</b>.\n\n"
            "Теперь утренняя рассылка будет приходить "
            "даже когда событий на сегодня нет."
        )
    await message.answer(text, parse_mode="HTML")

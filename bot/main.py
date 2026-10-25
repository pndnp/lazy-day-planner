import asyncio
import logging

from aiogram import Bot
from aiogram.types import BotCommand

from bot import dp
from bot.config import BOT_TOKEN, SUMMARY_HOUR, SUMMARY_MINUTE
from bot.handlers import configure_router
from bot.migrations import apply_migrations
from bot.models import create_tables
from bot.scheduler import daily_summary


async def on_startup(bot: Bot) -> None:
    """Called when polling starts."""
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="add", description="Добавить событие"),
        BotCommand(command="today", description="Планы на сегодня"),
        BotCommand(command="tomorrow", description="Планы на завтра"),
        BotCommand(command="week", description="Планы на неделю"),
        BotCommand(command="next_week", description="Планы на след. неделю"),
        BotCommand(command="all", description="Все события"),
        BotCommand(command="del", description="Удалить событие"),
        BotCommand(command="skipempty", description="Пропустить рассылку"),
        BotCommand(command="deleteaccount", description="Удалить аккаунт"),
        BotCommand(command="help", description="Справка"),
        BotCommand(command="settings", description="Настройки"),
    ])


async def on_shutdown(bot: Bot) -> None:
    """Called when polling stops."""


async def main() -> None:
    """Application entry point."""
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    dp.bot = bot

    await create_tables()
    await apply_migrations()
    configure_router(dp)

    from functools import partial

    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduled_job = partial(daily_summary, bot)

    scheduler = AsyncIOScheduler(event_loop=asyncio.get_running_loop())
    scheduler.add_job(scheduled_job, "cron", hour=SUMMARY_HOUR, minute=SUMMARY_MINUTE)
    scheduler.start()

    await on_startup(bot)
    await dp.start_polling(bot)
    await on_shutdown(bot)
    scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())

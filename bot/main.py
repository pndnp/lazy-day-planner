import asyncio
import logging
import ssl as ssl_module

from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from typing import TYPE_CHECKING

from bot import dp
from bot.app_server import create_aiohttp_app
from bot.config import (
    BOT_TOKEN,
    SUMMARY_HOUR,
    SUMMARY_MINUTE,
    SSL_CERT_PATH,
    SSL_KEY_PATH,
    TELEGRAM_WEBHOOK_URL,
)
from bot.handlers import configure_router
from bot.migrations import apply_migrations
from bot.models import create_tables
from bot.scheduler import daily_summary

WEBHOOK_PATH = "/webhook"


if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def on_startup(bot: Bot) -> None:
    """Register bot commands when application starts."""
    await bot.set_my_commands(
        [
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
        ]
    )


async def on_shutdown(bot: Bot) -> None:
    """Cleanup when application shuts down."""


async def main() -> None:
    """Application entry point."""
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required")

    bot = Bot(token=BOT_TOKEN)

    await create_tables()
    await apply_migrations()
    configure_router(dp)

    scheduler = _create_scheduler(bot)

    use_webhook = False
    if TELEGRAM_WEBHOOK_URL and not any(
        host in TELEGRAM_WEBHOOK_URL.lower()
        for host in ("localhost", "127.0.0.1", "[::1]", "0.0.0.0")
    ):
        logging.info("Starting in webhook mode: %s", TELEGRAM_WEBHOOK_URL)
        await bot.set_webhook(url=TELEGRAM_WEBHOOK_URL)
        use_webhook = True
    else:
        logging.info(
            "Starting in polling mode (webhook URL not configured or uses local address)"
        )

    await on_startup(bot)

    aiohttp_app = create_aiohttp_app(bot, dp)
    setup_application(aiohttp_app, dp, bot=bot)

    from aiohttp import web

    if use_webhook:
        webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_handler.register(aiohttp_app, path=WEBHOOK_PATH)

        ssl_context = None
        if SSL_CERT_PATH and SSL_KEY_PATH:
            ssl_context = ssl_module.SSLContext(ssl_module.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(certfile=SSL_CERT_PATH, keyfile=SSL_KEY_PATH)

        await web._run_app(
            aiohttp_app,
            host="0.0.0.0",
            port=80,
            reuse_port=True,
            ssl_context=ssl_context,
        )
    else:
        asyncio.create_task(dp.start_polling(bot, timeout=60))
        await web._run_app(aiohttp_app, host="0.0.0.0", port=80, reuse_port=True)

    await on_shutdown(bot)
    scheduler.shutdown(wait=False)


def _create_scheduler(bot: "Bot") -> "AsyncIOScheduler":  # noqa: F821
    """Create and start the APScheduler with daily summary job."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from functools import partial

    scheduled_job = partial(daily_summary, bot)
    scheduler = AsyncIOScheduler(event_loop=asyncio.get_running_loop())
    scheduler.add_job(scheduled_job, "cron", hour=SUMMARY_HOUR, minute=SUMMARY_MINUTE)
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    asyncio.run(main())

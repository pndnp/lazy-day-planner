from aiogram import Router

from bot.handlers.add import add_router
from bot.handlers.settings import settings_router
from bot.handlers.start import start_router
from bot.handlers.view import view_router


def configure_router(dp: Router) -> None:
    """Register all handler routers with the dispatcher."""
    dp.include_routers(start_router, add_router, settings_router, view_router)

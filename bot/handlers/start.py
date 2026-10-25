import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select

from bot.config import SUMMARY_HOUR, SUMMARY_MINUTE
from bot.db import async_session_factory
from bot.models import Event, User

start_router = Router()

logger = logging.getLogger(__name__)


@start_router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command - register user and show welcome message."""
    telegram_id = message.from_user.id

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=telegram_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)

    text = (
        "Привет! Я бот-напоминалка.\n\n"
        "Я помогу тебе планировать события на день и неделю вперед.\n\n"
        f"Я буду напоминать тебе о них утром в {SUMMARY_HOUR:02}:"
        f"{SUMMARY_MINUTE:02} каждого дня.\n\n"
        "Используй /add чтобы добавить событие,\n"
        "/today для просмотра планов на сегодня,\n"
        "/tomorrow — на завтра,\n"
        "/week — на текущую неделю.\n"
        "/skipempty — не присылать рассылку, если событий нет,\n"
        "/deleteaccount - удалить аккаунт из приложения,\n"
        "/help — справка по всем командам."
    )
    await message.answer(text)


@start_router.message(Command("deleteaccount"))
async def cmd_delete_account(message: Message) -> None:
    """Initiate account deletion flow."""
    # TODO: add GCAL sync integration, then add back GCAL-related lines
    text = (
        "⚠️ Удаление аккаунта\n\n"
        "Будет удалено:\n"
        "• Все ваши события\n"
        "• Настройки бота\n"
        # "• Токены Google Календаря\n\n"
        "Удаление необратимо!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Удалить аккаунт", callback_data="delete_account_confirm"),
            InlineKeyboardButton(text="Отмена", callback_data="delete_account_cancel"),
        ]
    ])
    await message.answer(text, reply_markup=kb)


@start_router.callback_query(F.data == "delete_account_confirm")
async def callback_delete_account_confirm(call) -> None:
    """Confirm and perform account deletion."""
    user_id = call.from_user.id
    try:
        async with async_session_factory() as session:
            user_result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_result.scalar_one_or_none()

            if user is None:
                await call.message.answer("Пользователь не найден.")
                return

            event_result = await session.execute(select(Event).where(Event.user_id == user.id))
            event_count = len(event_result.scalars().all())

            logger.info("Deleting user %d with %d events", user.id, event_count)

            await session.delete(user)
            await session.commit()

            # TODO: add GCAL sync integration, then append GCAL message
            success_msg = "Аккаунт удалён. Все данные успешно удалены."
            await call.message.answer(success_msg)
    except Exception:
        logger.exception("Failed to delete user %d", user_id)
        await call.message.answer("Произошла ошибка при удалении аккаунта.")


@start_router.callback_query(F.data == "delete_account_cancel")
async def callback_delete_account_cancel(call) -> None:
    """Cancel account deletion."""
    await call.message.answer("Удаление отменено. Аккаунт не удалён.")

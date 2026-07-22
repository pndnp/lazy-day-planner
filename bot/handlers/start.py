from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import SUMMARY_HOUR, SUMMARY_MINUTE

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command - register user and show welcome message."""
    text = (
        "Привет! Я бот-напоминалка.\n\n"
        "Я помогу тебе планировать события на день и неделю вперед.\n\n"
        f"Я буду напоминать тебе о них утром в {SUMMARY_HOUR:02}:"
        f"{SUMMARY_MINUTE:02} каждого дня.\n\n"
        "Используй /add чтобы добавить событие,\n"
        "/today для просмотра планов на сегодня,\n"
        "/tomorrow — на завтра,\n"
        "/week — на текущую неделю,\n"
        "/next_week — на следующую неделю,\n"
        "/skipempty — не присылать рассылку, если событий нет,\n"
        "/help — справка по командам."
    )
    await message.answer(text)

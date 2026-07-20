from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command - register user and show welcome message."""
    text = (
        "Привет! Я бот-напоминалка.\n\n"
        "Я помогу тебе планировать события на день и неделю вперед.\n\n"
        "Используйте /add чтобы добавить событие,\n"
        "/today для просмотра планов на сегодня,\n"
        "/tomorrow — на завтра,\n"
        "/week — на текущую неделю,\n"
        "/next_week — на следующую неделю.\n"
        "/help — справка по командам."
    )
    await message.answer(text)

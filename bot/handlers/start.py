from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command - register user and show welcome message."""
    text = (
        "Привет! \n"
        "Чтобы твой день был максимально ленивым, спланируй предстоящие события и расслабься, а я буду напоминать тебе о них утром каждого дня.\n\n"
        "Используй /add чтобы добавить событие,\n"
        "/today для просмотра планов на сегодня,\n"
        "/tomorrow — на завтра,\n"
        "/week — на текущую неделю,\n"
        "/next_week — на следующую неделю.\n"
        "/help — справка по командам."
    )
    await message.answer(text)

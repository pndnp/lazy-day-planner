import datetime as dt

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from bot.config import DATE_FMT, WEEKDAY_SHORT
from bot.db import async_session_factory
from bot.fsm import NewEventState
from bot.models import Event, User

add_router = Router()


def _cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="cancel_new_event")]
    ])


async def _get_or_create_user(user_id: int) -> User:
    """Get an existing user or create a new one."""
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=user_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


@add_router.message(Command("add"))
async def cmd_add(message: types.Message, state: FSMContext):
    """Start the event creation wizard."""
    await state.set_state(NewEventState.waiting_for_title)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="cancel_new_event")]
    ])
    await message.answer("Введите название события:", reply_markup=kb)


@add_router.message(NewEventState.waiting_for_title)
async def collect_title(message: types.Message, state: FSMContext):
    """Collect and validate event title."""
    if not message.text or not message.text.strip():
        await message.reply("Название не может быть пустым.")
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(NewEventState.waiting_for_date)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="cancel_new_event")]
    ])
    await message.answer("Формат даты и времени: dd.mm.yyyy HH:MM", reply_markup=kb)


@add_router.message(NewEventState.waiting_for_date)
async def collect_date(message: types.Message, state: FSMContext):
    """Collect, validate and store the event date/time."""
    raw = message.text.strip()
    try:
        parsed = dt.datetime.strptime(raw, DATE_FMT)
    except ValueError:
        await message.reply("Неверный формат. Формат: dd.mm.yyyy HH:MM")
        return
    await state.update_data(date_time=parsed.strftime(DATE_FMT))
    await state.set_state(NewEventState.waiting_for_location)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_loc"),
         InlineKeyboardButton(text="Отменить", callback_data="cancel_new_event")]
    ])
    await message.answer("Укажите место:", reply_markup=kb)


@add_router.callback_query(F.data == "skip_loc", NewEventState.waiting_for_location)
async def skip_location(callback_query: types.CallbackQuery, state: FSMContext):
    """Skip location input and save the event."""
    await callback_query.answer()
    await state.update_data(location=None)
    # ВАЖНО: получить ID пользователя из callback_query, а не из message!
    await _save_event(callback_query.message, state, callback_query.from_user.id)


@add_router.message(NewEventState.waiting_for_location)
async def collect_location(message: types.Message, state: FSMContext):
    """Collect and store event location."""
    await state.update_data(location=message.text.strip() or None)
    await _save_event(message, state, message.from_user.id)


@add_router.callback_query(F.data == "cancel_new_event")
async def cancel_new_event(callback_query: types.CallbackQuery, state: FSMContext):
    """Cancel event creation and clear state."""
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer("Добавление события отменено.")


async def _save_event(message: types.Message, state: FSMContext, user_id: int):
    """Save the event to database and confirm to user."""
    data = await state.get_data()
    title = data["title"]
    date_time_str = data["date_time"]
    location = data.get("location")

    date_time = dt.datetime.strptime(date_time_str, DATE_FMT)

    user = await _get_or_create_user(user_id)

    event = Event(title=title, date_time=date_time, location=location, user=user)

    async with async_session_factory() as session:
        session.add(event)
        await session.commit()

    day_short = WEEKDAY_SHORT[date_time.weekday()]
    reply = f"Событие '{title}' добавлено на {date_time_str} ({day_short})"
    if location:
        reply += f" • {location}"
    await message.answer(reply)

    await state.clear()

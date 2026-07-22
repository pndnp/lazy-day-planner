import datetime as dt
from zoneinfo import ZoneInfo

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from bot.config import DATE_FMT, TIMEZONE, WEEKDAY_SHORT
from bot.db import async_session_factory
from bot.fsm import NewEventState
from bot.handlers.calendar import calendar_keyboard
from bot.models import Event, User

add_router = Router()


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
async def cmd_add(message: types.Message, state: FSMContext) -> None:
    """Start the event creation wizard."""
    await state.set_state(NewEventState.waiting_for_title)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="cancel_new_event")]
    ])
    await message.answer("Введите название события:", reply_markup=kb)


@add_router.message(NewEventState.waiting_for_title)
async def collect_title(message: types.Message, state: FSMContext) -> None:
    """Collect and validate event title, then show inline calendar."""
    if not message.text or not message.text.strip():
        await message.reply("Название не может быть пустым.")
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(NewEventState.waiting_for_date)
    kb = calendar_keyboard()
    await message.answer("Выберите дату события:", reply_markup=kb)


# ── Calendar callbacks ──

@add_router.callback_query(
    F.data.startswith("calprev_"), NewEventState.waiting_for_date
)
async def cal_prev(callback_query: types.CallbackQuery) -> None:
    """Show previous month in inline calendar."""
    _, ym = callback_query.data.split("_", 1)
    year, month = map(int, ym.split("-"))
    # callback data already carries the target month, no extra math needed
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(
        reply_markup=calendar_keyboard(year, month)
    )


@add_router.callback_query(
    F.data.startswith("calnext_"), NewEventState.waiting_for_date
)
async def cal_next(callback_query: types.CallbackQuery) -> None:
    """Show next month in inline calendar."""
    _, ym = callback_query.data.split("_", 1)
    year, month = map(int, ym.split("-"))
    # callback data already carries the target month, no extra math needed
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(
        reply_markup=calendar_keyboard(year, month)
    )


@add_router.callback_query(F.data == "calignore")
async def cal_ignore(callback_query: types.CallbackQuery) -> None:
    """Ignore clicks on header / empty cells."""
    await callback_query.answer()


@add_router.callback_query(
    F.data.startswith("caldate_"), NewEventState.waiting_for_date
)
async def cal_select_date(
    callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    """User picked a day from the calendar → ask for time via text."""
    _, date_str = callback_query.data.split("_", 1)
    selected = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
    await state.update_data(event_date=selected.strftime("%d.%m.%Y"))
    await state.set_state(NewEventState.waiting_for_time)
    await callback_query.answer()
    await callback_query.message.edit_text(
        text="Введите время <code>hh:mm</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel_new_event")]
        ]),
    )


@add_router.callback_query(
    F.data.startswith("calquick_"), NewEventState.waiting_for_date
)
async def cal_quick_date(
    callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    """Quick pick today or tomorrow."""
    _, key = callback_query.data.split("_", 1)
    today = dt.datetime.now(ZoneInfo(TIMEZONE)).date()
    if key == "today":
        selected = today
    else:
        selected = today + dt.timedelta(days=1)
    await state.update_data(event_date=selected.strftime("%d.%m.%Y"))
    await state.set_state(NewEventState.waiting_for_time)
    await callback_query.answer()
    await callback_query.message.edit_text(
        text="Введите время <code>hh:mm</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel_new_event")]
        ]),
    )


# ── Time callback ──

@add_router.message(NewEventState.waiting_for_time)
async def collect_time(message: types.Message, state: FSMContext) -> None:
    """Collect and validate the time from user text input."""
    raw = message.text.strip()
    try:
        time_part = dt.datetime.strptime(raw, "%H:%M").time()
    except ValueError:
        await message.reply(
            "Неверный формат. Введите время <code>hh:mm</code>",
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    date_str = data["event_date"]
    raw_dt = f"{date_str} {time_part.strftime('%H:%M')}"

    try:
        parsed = dt.datetime.strptime(raw_dt, DATE_FMT)
    except ValueError:
        await message.reply("Ошибка формирования даты.")
        return

    await state.update_data(date_time=parsed.strftime(DATE_FMT))
    await state.set_state(NewEventState.waiting_for_location)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_loc"),
         InlineKeyboardButton(text="Отменить", callback_data="cancel_new_event")]
    ])
    await message.answer("Укажите место:", reply_markup=kb)


# ── Location (same flow as before) ──

@add_router.callback_query(F.data == "skip_loc", NewEventState.waiting_for_location)
async def skip_location(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """Skip location input and save the event."""
    await callback_query.answer()
    await state.update_data(location=None)
    await _save_event(callback_query.message, state, callback_query.from_user.id)


@add_router.message(NewEventState.waiting_for_location)
async def collect_location(message: types.Message, state: FSMContext) -> None:
    """Collect and store event location."""
    await state.update_data(location=message.text.strip() or None)
    await _save_event(message, state, message.from_user.id)


@add_router.callback_query(F.data == "cancel_new_event")
async def cancel_new_event(
    callback_query: types.CallbackQuery, state: FSMContext,
) -> None:
    """Cancel event creation and clear state."""
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer("Добавление события отменено.")


async def _save_event(message: types.Message, state: FSMContext, user_id: int) -> None:
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
    reply = f"Событие '{title}' добавлено на {day_short} {date_time_str}"

    await message.answer(reply)

    await state.clear()

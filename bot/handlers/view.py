import datetime as dt
import logging
from zoneinfo import ZoneInfo

from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select, delete

from bot.config import DATE_FMT, TIMEZONE, WEEKDAY_SHORT
from bot.db import async_session_factory
from bot.models import Event, User

view_router = Router()
logger = logging.getLogger(__name__)


@view_router.message(Command("today"))
async def cmd_today(message: types.Message):
    """Show events for today."""
    await _show_events(message)


@view_router.message(Command("tomorrow"))
async def cmd_tomorrow(message: types.Message):
    """Show events for tomorrow."""
    await _show_events(message, day="tomorrow")


@view_router.message(Command("week"))
async def cmd_week(message: types.Message):
    """Show events for current week."""
    logger.info(f"cmd_week: telegram_id={message.from_user.id}, text='{message.text}'")
    await _show_events(message, period="week")


@view_router.message(Command("next_week"))
async def cmd_next_week(message: types.Message):
    """Show events for next week."""
    logger.info(f"cmd_next_week: telegram_id={message.from_user.id}, text='{message.text}'")
    await _show_events(message, period="next_week")


@view_router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Show help message with all available commands."""
    text = (
        "Список доступных команд:\n\n"
        "/start — Приветствие и регистрация.\n"
        "/add — Добавить новое событие.\n"
        "/today — Просмотр событий на сегодня.\n"
        "/tomorrow — Просмотр событий на завтра.\n"
        "/week — Просмотр событий на текущую неделю.\n"
        "/del <id> — Удалить событие по его ID."
    )
    await message.answer(text)


@view_router.message(Command("del"))
async def cmd_del(message: types.Message):
    """Delete an event by its ID."""
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.reply("Используйте: /del <ID события>")
        return
    try:
        event_id = int(parts[1])
    except ValueError:
        await message.reply("Используйте: /del <ID события>")
        return

    telegram_id = message.from_user.id
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    if user is None:
        return

    async with async_session_factory() as session:
        result = await session.execute(
            select(Event).where(Event.id == event_id, Event.user_id == user.id)
        )
        event = result.scalar_one_or_none()

    if event is None:
        await message.reply(f"Событие с ID {event_id} не найдено.")
        return

    async with async_session_factory() as session:
        await session.execute(delete(Event).where(Event.id == event_id, Event.user_id == user.id))
        await session.commit()

    await message.reply(f"Событие '{event.title}' удалено.")


async def _show_events(
    message: types.Message, day: str = "today", period: str = ""
) -> None:
    """Query and display events based on the selected day/period."""
    now = dt.datetime.now(ZoneInfo(TIMEZONE)).replace(tzinfo=None)
    telegram_id = message.from_user.id

    logger.info(f"_show_events: telegram_id={telegram_id}, day={day}, period='{period}', now={now.date()}")

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    if user is None:
        return

    async with async_session_factory() as session:
        result = await session.execute(select(Event).where(Event.user_id == user.id))
        events = result.scalars().all()

    logger.info(f"_show_events: found {len(events)} events for user {user.id}")

    if not events:
        labels = {"today": "сегодня", "tomorrow": "завтра"}
        if period == "next_week":
            label = "на следующей неделе"
        elif period == "week":
            label = "на этой неделе"
        else:
            label = labels.get(day, "")
        await message.answer(f"Нет событий на {label}")
        return

    filtered = []
    for ev in events:
        d = ev.date_time.date() if hasattr(ev.date_time, 'date') else ev.date_time
        
        if period == "week":
            monday = now.date() - dt.timedelta(days=now.weekday())
            sunday = monday + dt.timedelta(days=6)
            if monday <= d <= sunday:
                filtered.append(ev)
        elif period == "next_week":
            monday = now.date() - dt.timedelta(days=now.weekday()) + dt.timedelta(weeks=1)
            sunday = monday + dt.timedelta(days=6)
            if monday <= d <= sunday:
                filtered.append(ev)
        elif day == "today":
            if d == now.date():
                filtered.append(ev)
        elif day == "tomorrow":
            tomorrow = now.date() + dt.timedelta(days=1)
            if d == tomorrow:
                filtered.append(ev)
        
        logger.info(f"  event {ev.title}: date={d} -> filtered={ev in filtered}")

    filtered.sort(key=lambda e: e.date_time)
    
    logger.info(f"_show_events: filtered {len(filtered)} events for period='{period}'")

    if not filtered:
        labels = {"today": "сегодня", "tomorrow": "завтра"}
        if period == "next_week":
            label = "на следующей неделе"
        elif period == "week":
            label = "на этой неделе"
        else:
            label = labels.get(day, "")
        await message.answer(f"Нет событий на {label}")
        return

    if period == "next_week":
        header = "События на следующей неделе:"
    elif period == "week":
        header = "События на этой неделе:"
    else:
        header = f"События на {'сегодня' if day == 'today' else 'завтра'}:"
    lines = [header, "", ]
    for ev in filtered:
        day_short = WEEKDAY_SHORT[ev.date_time.weekday()]  # пн/вт/ср...
        text = f"{day_short} {ev.date_time.strftime(DATE_FMT)} — {ev.title}"
        if ev.location:
            text += f" • {ev.location}"
        lines.append(text)
    
    logger.info(f"_show_events: sending response with {len(lines)-2} items")
    await message.answer("\n".join(lines))

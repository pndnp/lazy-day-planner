import datetime as dt
import logging
from zoneinfo import ZoneInfo

from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import delete, select

from bot.config import DATE_FMT, TIMEZONE, WEEKDAY_SHORT
from bot.db import async_session_factory
from bot.models import Event, User

logger = logging.getLogger(__name__)
view_router = Router()


@view_router.message(Command("today"))
async def cmd_today(message: types.Message):
    """Show events for today."""
    logger.info("cmd_today received from user %s", message.from_user.id)
    try:
        await _show_events(message, day="today")
        logger.info("cmd_today responded successfully")
    except Exception:
        logger.exception("cmd_today failed")


@view_router.message(Command("tomorrow"))
async def cmd_tomorrow(message: types.Message):
    """Show events for tomorrow."""
    logger.info("cmd_tomorrow received from user %s", message.from_user.id)
    try:
        await _show_events(message, day="tomorrow")
        logger.info("cmd_tomorrow responded successfully")
    except Exception:
        logger.exception("cmd_tomorrow failed")


@view_router.message(Command("week"))
async def cmd_week(message: types.Message):
    """Show events for current week."""
    logger.info("cmd_week received from user %s", message.from_user.id)
    try:
        await _show_events(message, period="week")
        logger.info("cmd_week responded successfully")
    except Exception:
        logger.exception("cmd_week failed")


@view_router.message(Command("next_week"))
async def cmd_next_week(message: types.Message):
    """Show events for next week."""
    logger.info("cmd_next_week received from user %s", message.from_user.id)
    try:
        await _show_events(message, period="next_week")
        logger.info("cmd_next_week responded successfully")
    except Exception:
        logger.exception("cmd_next_week failed")


@view_router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Show help message with all available commands."""
    logger.info("cmd_help received from user %s", message.from_user.id)
    try:
        text = (
            "Список доступных команд:\n\n"
            "/start — Приветствие и регистрация\n"
            "/add — Добавить новое событие\n"
            "/today — Просмотр событий на сегодня\n"
            "/tomorrow — Просмотр событий на завтра\n"
            "/week — Просмотр событий на текущую неделю\n"
            "/next_week — Просмотр событий на следующую неделю\n"
            "/all — Список всех событий\n"
            "/skipempty — Не присылать пустую рассылку\n"
            "/del <id> — Удалить событие по его ID"
        )
        await message.answer(text)
        logger.info("cmd_help responded successfully")
    except Exception:
        logger.exception("cmd_help failed")


@view_router.message(Command("del"))
async def cmd_del(message: types.Message):
    """Delete an event by its ID."""
    logger.info("cmd_del received from user %s", message.from_user.id)
    try:
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
            await message.reply("Пользователь не найден. Отправьте /start")
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
        logger.info("cmd_del responded successfully")
    except Exception:
        logger.exception("cmd_del failed")


@view_router.message(Command("all"))
async def cmd_all(message: types.Message):
    """Show all events."""
    logger.info("cmd_all received from user %s", message.from_user.id)
    try:
        telegram_id = message.from_user.id

        async with async_session_factory() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()

        if user is None:
            await message.reply("Пользователь не найден. Отправьте /start")
            return

        async with async_session_factory() as session:
            result = await session.execute(select(Event).where(Event.user_id == user.id))
            events = result.scalars().all()

        if not events:
            await message.answer("Нет планов")
            return

        events.sort(key=lambda e: e.date_time)
        lines = ["Все события:\n"]
        for ev in events:
            day_short = WEEKDAY_SHORT[ev.date_time.weekday()]
            text = f"{day_short} {ev.date_time.strftime(DATE_FMT)} {ev.title} ({ev.id})"
            lines.append(text)

        await message.answer("\n".join(lines))
        logger.info("cmd_all responded successfully")
    except Exception:
        logger.exception("cmd_all failed")


async def _show_events(
    message: types.Message, day: str = "", period: str = ""
) -> None:
    """Query and display events based on the selected day/period."""
    logger.info("_show_events called: day=%s, period=%s, user=%s", day, period, message.from_user.id)
    now = dt.datetime.now(ZoneInfo(TIMEZONE)).replace(tzinfo=None)
    telegram_id = message.from_user.id

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    if user is None:
        logger.info("User not found for telegram_id=%s", telegram_id)
        await message.answer("Пользователь не найден. Отправьте /start")
        return

    async with async_session_factory() as session:
        result = await session.execute(select(Event).where(Event.user_id == user.id))
        events = result.scalars().all()

    logger.info("Found %d events for user %s", len(events), user.id)

    if not events:
        labels = {"today": "сегодня", "tomorrow": "завтра"}
        if period == "next_week":
            label = "на следующую неделю"
        elif period == "week":
            label = "на эту неделю"
        else:
            label = labels.get(day, "")
        await message.answer(f"Нет планов на {label}")
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

    filtered.sort(key=lambda e: e.date_time)

    if not filtered:
        if day == "tomorrow":
            await message.answer("🎉 На завтра планов нет. Какой прекрасный день!")
            return
        if day == "today":
            await message.answer("🎉 На сегодня планов нет. Какой прекрасный день!")
            return
        labels = {"today": "сегодня", "tomorrow": "завтра"}
        if period == "next_week":
            label = "на следующую неделю"
        elif period == "week":
            label = "на эту неделю"
        else:
            label = labels.get(day, "")
        await message.answer(f"Нет планов на {label}")
        return

    if period == "next_week":
        header = "План на следующую неделю:"
    elif period == "week":
        header = "План на эту неделю:"
    else:
        header = f"План на {'сегодня' if day == 'today' else 'завтра'}:"
    lines = [header, "", ]
    for ev in filtered:
        day_short = WEEKDAY_SHORT[ev.date_time.weekday()]
        text = f"{day_short} {ev.date_time.strftime(DATE_FMT)} — {ev.title}"
        if ev.location:
            text += f" • {ev.location}"
        lines.append(text)

    await message.answer("\n".join(lines))

import datetime as dt
from zoneinfo import ZoneInfo

from aiogram import Bot
from sqlalchemy import select

from bot.config import DATE_FMT, TIMEZONE, WEEKDAY_SHORT
from bot.db import async_session_factory
from bot.models import Event, User


async def daily_summary(bot: Bot) -> None:
    """Send daily summary to all users with events for today and tomorrow."""
    now = dt.datetime.now(ZoneInfo(TIMEZONE)).replace(tzinfo=None)

    # Удаляем прошедшие события
    async with async_session_factory() as session:
        result = await session.execute(select(Event))
        events = result.scalars().all()
        deleted = 0
        for ev in events:
            if ev.date_time < now:
                await session.delete(ev)
                deleted += 1
        if deleted > 0:
            await session.commit()

    user_ids = []

    async with async_session_factory() as session:
        result = await session.execute(select(User.id))
        rows = result.all()
        user_ids = [row[0] for row in rows]

    if not user_ids:
        return

    messages_by_user: dict[int, list[str]] = {}

    for uid in user_ids:
        async with async_session_factory() as session:
            result = await session.execute(
                select(Event).where(Event.user_id == uid)
            )
            events = result.scalars().all()

        lines: list[str] = []

        today_events = sorted(
            [e for e in events if e.date_time.date() == now.date()],
            key=lambda e: e.date_time,
        )
        tomorrow_events = sorted(
            [
                e
                for e in events
                if e.date_time.date()
                == now.date() + dt.timedelta(days=1)
            ],
            key=lambda e: e.date_time,
        )

        if not today_events and not tomorrow_events:
            lines.append("🎉 Сегодня ничего нет. Какой прекрасный день!")

        if today_events:
            lines.append("Планы на сегодня:")
            for ev in today_events:
                day_short = WEEKDAY_SHORT[ev.date_time.weekday()]
                text = f"{day_short} {ev.date_time.strftime(DATE_FMT)} — {ev.title}"
                if ev.location:
                    text += f" • {ev.location}"
                lines.append(text)

        if tomorrow_events:
            lines.append("Планы на завтра:")
            for ev in tomorrow_events:
                day_short = WEEKDAY_SHORT[ev.date_time.weekday()]
                text = f"{day_short} {ev.date_time.strftime(DATE_FMT)} — {ev.title}"
                if ev.location:
                    text += f" • {ev.location}"
                lines.append(text)

        if lines:
            messages_by_user[uid] = lines


    telegram_ids: dict[int | None, int] = {}
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = result.scalars().all()
        for user in users:
            telegram_ids[user.id] = user.telegram_id

    for uid, msg_lines in messages_by_user.items():
        tid = telegram_ids.get(uid)
        if tid is None:
            continue
        try:
            await bot.send_message(
                chat_id=tid,
                text="\n".join(msg_lines),
            )
        except Exception:
            pass

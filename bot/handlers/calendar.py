"""Inline calendar and time keyboards for event creation."""

import calendar
import datetime as dt

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def _month_name(year: int, month: int) -> str:
    """Return Russian month-year header."""
    months = [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
    ]
    return f"{months[month - 1]} {year}"


def calendar_keyboard(
    year: int | None = None, month: int | None = None
) -> InlineKeyboardMarkup:
    """Generate inline calendar for a given month.

    Callback data format:
        calignore  — blank / padding cell
        calprev_YYYY-MM — previous month button
        calnext_YYYY-MM — next month button
        caldate_YYYY-MM-DD — selected day
    """
    now = dt.datetime.now()
    year = year or now.year
    month = month or now.month

    keyboard: list[list[InlineKeyboardButton]] = []

    # Month navigation row
    today = dt.datetime.now().date()
    if month == 1:
        prev_month = dt.date(year - 1, 12, 1)
    else:
        prev_month = dt.date(year, month - 1, 1)

    if month == 12:
        next_month = dt.date(year + 1, 1, 1)
    else:
        next_month = dt.date(year, month + 1, 1)

    # If viewing the current month, disable the "<" arrow
    is_current_month = (year == today.year and month == today.month)
    prev_cd = (
        "calignore" if is_current_month
        else f"calprev_{prev_month.year:04d}-{prev_month.month:02d}"
    )

    keyboard.append(
        [
            InlineKeyboardButton(
                text=" " if is_current_month else "<",
                callback_data=prev_cd,
            ),
            InlineKeyboardButton(
                text=_month_name(year, month), callback_data="calignore"
            ),
            InlineKeyboardButton(
                text=">",
                callback_data=f"calnext_{next_month.year:04d}-{next_month.month:02d}",
            ),
        ]
    )

    # Weekday headers
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.append(
        [
            InlineKeyboardButton(text=day, callback_data="calignore")
            for day in week_days
        ]
    )

    # Days grid
    today = dt.datetime.now().date()
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row: list[InlineKeyboardButton] = []
        for day in week:
            if day == 0:
                row.append(
                    InlineKeyboardButton(text=" ", callback_data="calignore")
                )
            else:
                cell_date = dt.date(year, month, day)
                if cell_date < today:
                    row.append(
                        InlineKeyboardButton(
                            text="·",
                            callback_data="calignore",
                        )
                    )
                else:
                    row.append(
                        InlineKeyboardButton(
                            text=str(day),
                            callback_data=f"caldate_{year:04d}-{month:02d}-{day:02d}",
                        )
                    )
        keyboard.append(row)

    # Quick-pick + cancel row
    keyboard.append(
        [
            InlineKeyboardButton(text="Сегодня", callback_data="calquick_today"),
            InlineKeyboardButton(text="Завтра", callback_data="calquick_tomorrow"),
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(text="Отменить", callback_data="cancel_new_event")
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def time_keyboard() -> InlineKeyboardMarkup:
    """Generate inline keyboard with time options.

    Callback data: caltime_HH:MM
    """
    hours = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    minutes = ["00", "15", "30", "45"]

    keyboard: list[list[InlineKeyboardButton]] = []

    for h in hours:
        row: list[InlineKeyboardButton] = []
        for m in minutes:
            row.append(
                InlineKeyboardButton(
                    text=f"{h:02d}:{m}",
                    callback_data=f"caltime_{h:02d}:{m}",
                )
            )
        keyboard.append(row)

    keyboard.append(
        [
            InlineKeyboardButton(text="Отменить", callback_data="cancel_new_event")
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

"""Unit tests for daily summary logic (filtering, formatting, skip_empty)."""

import datetime as dt

from bot.config import DATE_FMT, WEEKDAY_SHORT


class MockEvent:
    """Lightweight mock for Event without SQLAlchemy."""

    def __init__(self, title: str, date_time: dt.datetime, location: str | None = None):
        self.title = title
        self.date_time = date_time
        self.location = location


class MockUser:
    """Lightweight mock for User without SQLAlchemy."""

    def __init__(self, telegram_id: int, settings: dict | None = None):
        self.telegram_id = telegram_id
        self._settings = settings or {}

    def get_setting(self, key: str, default: bool = False) -> bool:
        return self._settings.get(key, default)


def _filter_today_events(events: list[MockEvent], now: dt.datetime) -> list[MockEvent]:
    """Filter events for today (pure function extracted from scheduler)."""
    return sorted(
        [e for e in events if e.date_time.date() == now.date()],
        key=lambda e: e.date_time,
    )


def _is_expired(event: MockEvent, now: dt.datetime) -> bool:
    """Check if event is expired (passed)."""
    return event.date_time < now


def _format_summary_lines(
    today_events: list[MockEvent],
    now: dt.datetime,
    skip_empty: bool,
) -> list[str]:
    """Format summary lines (pure function extracted from scheduler)."""
    lines: list[str] = []

    if not today_events and skip_empty:
        return []  # skip sending

    if not today_events:
        lines.append("🎉 На сегодня планов нет. Какой прекрасный день!")
        return lines

    lines.append("План на сегодня:")
    for ev in today_events:
        day_short = WEEKDAY_SHORT[ev.date_time.weekday()]
        text = f"{day_short} {ev.date_time.strftime(DATE_FMT)} — {ev.title}"
        if ev.location:
            text += f" • {ev.location}"
        lines.append(text)

    return lines


# ── Tests ──


def test_skip_empty_returns_empty_lines():
    """User with skip_empty=True and no events → no lines to send."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events: list[MockEvent] = []
    lines = _format_summary_lines(events, now, skip_empty=True)
    assert lines == []


def test_no_events_sends_message():
    """User with skip_empty=False and no events → gets message."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events: list[MockEvent] = []
    lines = _format_summary_lines(events, now, skip_empty=False)
    assert lines == ["🎉 На сегодня планов нет. Какой прекрасный день!"]


def test_summary_format_with_event():
    """Event on today → formatted with day, date, title."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events = [MockEvent("Стоматолог", dt.datetime(2026, 7, 21, 14, 30))]
    lines = _format_summary_lines(events, now, skip_empty=False)

    assert "План на сегодня:" in lines
    assert "вт 21.07.2026 14:30 — Стоматолог" in lines


def test_summary_format_with_location():
    """Event with location → adds ' • Location'."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events = [MockEvent("Встреча", dt.datetime(2026, 7, 21, 10, 0), "Офис")]
    lines = _format_summary_lines(events, now, skip_empty=False)

    assert "вт 21.07.2026 10:00 — Встреча • Офис" in lines


def test_summary_events_sorted_by_time():
    """Multiple events sorted by time."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events = [
        MockEvent("Обед", dt.datetime(2026, 7, 21, 13, 0)),
        MockEvent("Утро", dt.datetime(2026, 7, 21, 9, 0)),
    ]
    today_events = _filter_today_events(events, now)
    lines = _format_summary_lines(today_events, now, skip_empty=False)

    # Morning should come before lunch (lines[0] = header, lines[1] = "", lines[2+] = events)
    morning_idx = next(i for i, line in enumerate(lines) if "Утро" in line)
    lunch_idx = next(i for i, line in enumerate(lines) if "Обед" in line)
    assert morning_idx < lunch_idx


def test_events_from_other_days_not_included():
    """Events on different days are excluded from summary."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events = [
        MockEvent("Вчера", dt.datetime(2026, 7, 20, 10, 0)),
        MockEvent("Завтра", dt.datetime(2026, 7, 22, 10, 0)),
    ]
    today_events = _filter_today_events(events, now)
    lines = _format_summary_lines(today_events, now, skip_empty=False)
    assert lines == ["🎉 На сегодня планов нет. Какой прекрасный день!"]


def test_expired_event_filtering():
    """Expired events are detected and filtered."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events = [
        MockEvent("Прошлое", dt.datetime(2026, 7, 20, 10, 0)),
        MockEvent("Будущее", dt.datetime(2026, 7, 25, 10, 0)),
    ]

    expired = [_is_expired(e, now) for e in events]
    assert expired[0] is True  # past
    assert expired[1] is False  # future


def test_today_event_not_expired():
    """Today's events are not expired."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    event = MockEvent("Сегодняшний", dt.datetime(2026, 7, 21, 14, 0))
    assert _is_expired(event, now) is False


def test_same_time_event_not_expired():
    """Event at exactly now time is not expired."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    event = MockEvent("Текущий", now)
    assert _is_expired(event, now) is False


def test_weekday_correct_for_today():
    """Tuesday 21 July 2026 has correct weekday short name."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events = [MockEvent("Тест", now)]
    lines = _format_summary_lines(events, now, skip_empty=False)

    # 21 July 2026 is Tuesday
    assert any("вт" in line for line in lines)


def test_multiple_users_different_skip():
    """Different skip_empty settings for different users."""
    user_a = MockUser(1, settings={"skip_empty": True})
    user_b = MockUser(2, settings={"skip_empty": False})

    assert user_a.get_setting("skip_empty") is True
    assert user_b.get_setting("skip_empty", False) is False


def test_summary_header_present():
    """Summary header is 'План на сегодня:'."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events = [MockEvent("Событие", dt.datetime(2026, 7, 21, 10, 0))]
    lines = _format_summary_lines(events, now, skip_empty=False)

    assert "План на сегодня:" in lines


def test_empty_event_title():
    """Event with empty title still appears."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events = [MockEvent("", dt.datetime(2026, 7, 21, 10, 0))]
    lines = _format_summary_lines(events, now, skip_empty=False)
    assert any("— " in line for line in lines)


def test_future_event_not_filtered():
    """Future events in the list (not today) are correctly excluded from filtered."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events = [
        MockEvent("Прошлое 1", dt.datetime(2026, 7, 20, 10, 0)),
        MockEvent("Сегодня", dt.datetime(2026, 7, 21, 14, 0)),
        MockEvent("Прошлое 2", dt.datetime(2026, 7, 19, 9, 0)),
    ]
    today_events = _filter_today_events(events, now)
    assert len(today_events) == 1
    assert today_events[0].title == "Сегодня"


def test_filter_by_exact_date():
    """Filter matches date only, not time."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    events = [
        MockEvent("Утро", dt.datetime(2026, 7, 21, 6, 0)),
        MockEvent("Вечер", dt.datetime(2026, 7, 21, 23, 59)),
    ]
    today_events = _filter_today_events(events, now)
    assert len(today_events) == 2


def test_event_in_same_minute_not_expired():
    """Event at exactly the summary time is not considered expired."""
    now = dt.datetime(2026, 7, 21, 8, 8)
    event = MockEvent("Своевременное", dt.datetime(2026, 7, 21, 8, 8))
    assert _is_expired(event, now) is False
    today_events = _filter_today_events([event], now)
    assert len(today_events) == 1

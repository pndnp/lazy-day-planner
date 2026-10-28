import datetime as dt


def _compute_range(now_date_str: str, event_dates: list[str]) -> dict:
    now = dt.datetime.strptime(now_date_str, "%Y-%m-%d").date()

    w_monday = now - dt.timedelta(days=now.weekday())
    w_sunday = w_monday + dt.timedelta(days=6)
    nw_monday = w_monday + dt.timedelta(weeks=1)
    nw_sunday = nw_monday + dt.timedelta(days=6)

    events = {}
    for ev in event_dates:
        if isinstance(ev, str):
            d = dt.datetime.strptime(ev, "%Y-%m-%d %H:%M").date()
        else:
            d = ev

        in_week_w = w_monday <= d <= w_sunday
        in_week_nw = nw_monday <= d <= nw_sunday

        events[ev] = {
            "in_week": in_week_w,
            "in_next": in_week_nw,
        }

    return {
        "monday_week": w_monday,
        "sunday_week": w_sunday,
        "monday_next": nw_monday,
        "sunday_next": nw_sunday,
        "events": events,
    }


def test_range_tuesday():
    """Сегодня вторник 21 июля 2026 (weekday=2)"""
    res = _compute_range(
        "2026-07-21",
        [
            "2026-07-21 18:30",
            "2026-07-23 13:00",
        ],
    )

    assert res["monday_week"] == dt.date(2026, 7, 20)
    assert res["sunday_week"] == dt.date(2026, 7, 26)
    assert res["monday_next"] == dt.date(2026, 7, 27)
    assert res["sunday_next"] == dt.date(2026, 8, 2)
    assert res["events"]["2026-07-21 18:30"]["in_week"] is True
    assert res["events"]["2026-07-23 13:00"]["in_week"] is True


def test_range_monday():
    """Сегодня понедельник 20 июля 2026 (weekday=0)"""
    res = _compute_range(
        "2026-07-20",
        [
            "2026-07-20 18:30",
            "2026-07-23 13:00",
        ],
    )

    assert res["monday_week"] == dt.date(2026, 7, 20)
    assert res["sunday_week"] == dt.date(2026, 7, 26)
    assert res["events"]["2026-07-20 18:30"]["in_week"] is True
    assert res["events"]["2026-07-23 13:00"]["in_week"] is True


def test_range_next_week():
    """События следующей недели не должны попадать в текущую"""
    res = _compute_range(
        "2026-07-21",
        [
            "2026-07-28 10:00",
            "2026-07-29 15:00",
        ],
    )

    assert res["events"]["2026-07-28 10:00"]["in_week"] is False
    assert res["events"]["2026-07-28 10:00"]["in_next"] is True
    assert res["events"]["2026-07-29 15:00"]["in_next"] is True


def test_range_empty():
    """Нет событий — события должны быть пустым словарём"""
    res = _compute_range("2026-07-21", [])
    assert res["events"] == {}

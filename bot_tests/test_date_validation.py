"""Unit tests for date/time parsing and validation used by event creation."""

import datetime as dt

from bot.config import DATE_FMT


def test_parse_valid_datetime():
    """Valid date/time string parses correctly."""
    parsed = dt.datetime.strptime("15.08.2026 14:30", DATE_FMT)
    assert parsed.year == 2026
    assert parsed.month == 8
    assert parsed.day == 15
    assert parsed.hour == 14
    assert parsed.minute == 30


def test_parse_invalid_date():
    """Invalid date raises ValueError."""
    try:
        dt.datetime.strptime("32.13.2026 25:61", DATE_FMT)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_parse_invalid_format():
    """Wrong format raises ValueError."""
    try:
        dt.datetime.strptime("2026-08-15 14:30", DATE_FMT)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_parse_invalid_time():
    """Invalid time raises ValueError."""
    try:
        dt.datetime.strptime("15.08.2026 25:00", DATE_FMT)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_parse_time_only():
    """Parsing time-only string %H:%M."""
    parsed = dt.datetime.strptime("14:30", "%H:%M")
    assert parsed.hour == 14
    assert parsed.minute == 30


def test_combine_date_and_time():
    """Combining date and time strings produces correct datetime."""
    date_str = "15.08.2026"
    time_str = "14:30"
    combined = f"{date_str} {time_str}"
    parsed = dt.datetime.strptime(combined, DATE_FMT)
    assert parsed == dt.datetime(2026, 8, 15, 14, 30)


def test_invalid_time_rejects_combined():
    """Invalid time in combined string raises ValueError."""
    date_str = "15.08.2026"
    time_str = "25:00"
    combined = f"{date_str} {time_str}"
    try:
        dt.datetime.strptime(combined, DATE_FMT)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_edge_case_midnight():
    """Midnight time 00:00 parses correctly."""
    parsed = dt.datetime.strptime("01.01.2026 00:00", DATE_FMT)
    assert parsed.hour == 0
    assert parsed.minute == 0


def test_edge_case_leap_year():
    """February 29 on leap year parses correctly."""
    parsed = dt.datetime.strptime("29.02.2024 12:00", DATE_FMT)
    assert parsed.year == 2024
    assert parsed.month == 2
    assert parsed.day == 29


def test_edge_case_non_leap_year():
    """February 29 on non-leap year raises ValueError."""
    try:
        dt.datetime.strptime("29.02.2025 12:00", DATE_FMT)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_strftime_roundtrip():
    """Formatting and parsing produces same datetime."""
    original = dt.datetime(2026, 7, 21, 18, 30)
    formatted = original.strftime(DATE_FMT)
    parsed = dt.datetime.strptime(formatted, DATE_FMT)
    assert parsed == original


def test_weekday_after_parsing():
    """Weekday is correct after parsing."""
    # 21 July 2026 is Tuesday (weekday=1)
    parsed = dt.datetime.strptime("21.07.2026 10:00", DATE_FMT)
    assert parsed.weekday() == 1  # Tuesday


def test_parse_empty_string():
    """Empty string raises ValueError."""
    try:
        dt.datetime.strptime("", DATE_FMT)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_parse_partial_string():
    """Partial date string raises ValueError."""
    try:
        dt.datetime.strptime("15.08", DATE_FMT)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

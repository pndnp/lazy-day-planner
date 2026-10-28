"""Unit tests for User model settings management."""

import json

from bot.models import User


def test_settings_default_empty():
    """New user has empty settings dict."""
    user = User(telegram_id=12345)
    assert user.settings == {}


def test_settings_from_json():
    """Settings property parses JSON correctly."""
    user = User(telegram_id=12345, settings_json='{"skip_empty": true}')
    assert user.settings == {"skip_empty": True}


def test_settings_set_and_serialize():
    """Setting a value updates settings_json."""
    user = User(telegram_id=12345)
    user.settings = {"skip_empty": True, "lang": "ru"}
    assert user.settings_json == json.dumps(
        {"skip_empty": True, "lang": "ru"}, ensure_ascii=False
    )


def test_get_setting_default():
    """get_setting returns default for missing key."""
    user = User(telegram_id=12345)
    assert user.get_setting("skip_empty", False) is False


def test_get_setting_existing():
    """get_setting returns the stored value."""
    user = User(telegram_id=12345, settings_json='{"skip_empty": true}')
    assert user.get_setting("skip_empty", False) is True


def test_set_setting_updates_value():
    """set_setting adds key to settings."""
    user = User(telegram_id=12345)
    user.set_setting("skip_empty", True)
    assert user.get_setting("skip_empty") is True


def test_set_setting_overwrites():
    """set_setting overwrites existing value."""
    user = User(telegram_id=12345, settings_json='{"skip_empty": false}')
    user.set_setting("skip_empty", True)
    assert user.get_setting("skip_empty") is True


def test_toggle_setting_from_false_to_true():
    """toggle_setting flips from default False to True."""
    user = User(telegram_id=12345)
    result = user.toggle_setting("skip_empty", default=False)
    assert result is True
    assert user.get_setting("skip_empty") is True


def test_toggle_setting_from_true_to_false():
    """toggle_setting flips from True back to False."""
    user = User(telegram_id=12345, settings_json='{"skip_empty": true}')
    result = user.toggle_setting("skip_empty", default=True)
    assert result is False
    assert user.get_setting("skip_empty") is False


def test_toggle_setting_returns_new_value():
    """toggle_setting returns the new boolean value."""
    user = User(telegram_id=12345)
    val1 = user.toggle_setting("test_key")
    val2 = user.toggle_setting("test_key")
    assert val1 is True
    assert val2 is False


def test_settings_json_invalid_json():
    """Invalid JSON returns empty dict."""
    user = User(telegram_id=12345, settings_json="not json")
    assert user.settings == {}


def test_settings_json_none():
    """None settings_json returns empty dict."""
    user = User(telegram_id=12345, settings_json=None)
    assert user.settings == {}

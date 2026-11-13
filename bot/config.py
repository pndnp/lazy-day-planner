import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
TIMEZONE = "Europe/Moscow"  # пояс рассылки 08:00
DATE_FMT = "%d.%m.%Y %H:%M"  # формат ввода даты от пользователя
WEEK_DAY = 0  # 0 == понедельник (Python weekday())
SUMMARY_HOUR = 8  # час ежедневной рассылки
SUMMARY_MINUTE = 8
WEEKDAY_SHORT = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

# Webhook configuration
TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
SSL_CERT_PATH: str | None = (
    os.getenv("SSL_CERT_PATH")
    if os.getenv("SSL_CERT_PATH") and os.path.exists(os.getenv("SSL_CERT_PATH"))
    else None
)
SSL_KEY_PATH: str | None = (
    os.getenv("SSL_KEY_PATH")
    if os.getenv("SSL_KEY_PATH") and os.path.exists(os.getenv("SSL_KEY_PATH"))
    else None
)

# OAuth (not currently implemented)
# OAUTH_CALLBACK_URL: str | None = os.getenv("OAUTH_CALLBACK_URL") or None


# def get_oauth_callback_url() -> str | None:
#     """Derive OAuth callback URL from TELEGRAM_WEBHOOK_URL."""
#     if not TELEGRAM_WEBHOOK_URL:
#         return None
#     return f"{TELEGRAM_WEBHOOK_URL.rstrip('/')}/oauth/callback"

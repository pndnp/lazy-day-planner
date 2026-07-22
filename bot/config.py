import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN  = os.getenv("BOT_TOKEN")
DB_PATH    = os.getenv("DB_PATH")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
TIMEZONE   = "Europe/Moscow"                      # пояс рассылки 08:00
DATE_FMT   = "%d.%m.%Y %H:%M"                     # формат ввода даты от пользователя
WEEK_DAY   = 0                                    # 0 == понедельник (Python weekday())
SUMMARY_HOUR   = 8                                # час ежедневной рассылки
SUMMARY_MINUTE = 8
WEEKDAY_SHORT = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

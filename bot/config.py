BOT_TOKEN  = "8703511334:AAEQ9kqgRD0dkhIxJkR0-MwDswuF3WsJr5A"
DB_PATH    = "events.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"   # путь от cwd проекта
TIMEZONE   = "Europe/Moscow"                      # пояс рассылки 08:00
DATE_FMT   = "%d.%m.%Y %H:%M"                    # формат ввода даты от пользователя
WEEK_DAY   = 0                                    # 0 == понедельник (Python weekday())

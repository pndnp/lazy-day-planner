# Agents Description

This repository contains a single Telegram bot project. The bot code lives under the `bot/` package and the overall architecture is documented in `README.md`. The bot implements:

- Event creation via a finite‑state‑machine wizard (`/add`).
- Daily summary at 08:08 using **APScheduler**.
- Multi‑user support through the `User` model.
- Persistence with **SQLite** (or PostgreSQL via `DB_URL`).

All interaction is handled by **aiogram 3**, and the database layer uses **SQLAlchemy [asyncio]**. See `README.md` for detailed installation and usage instructions.


# Instructions

Изучи описание и структуру проекта в README. Посмотри используемые глобальные переменные в bot/config.py и везде используй их, а не подставляй значения напрямую в код. При написании кода используй только английский и русский языки. *Удаляй неиспользуемые переменные и импорты из кода*. Проверяй линтером код.

Подходи к решению задачи вдумчиво, не спеши. Если задача большая и требует правок в нескольких файлах, сначала составь план того, что будешь делать и дождись одобрения. Если не находишь решения за несколько попыток, то остановись и скажи об этом, запроси уточнения или изменения запроса.





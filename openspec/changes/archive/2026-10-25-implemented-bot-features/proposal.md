# Implemented Bot Features

## Why
Задокументировать уже реализованный функционал бота-напоминалки для последующего архивирования и понимания текущего состояния системы.

## What Changes
Функционал уже реализован и задокументирован в виде OpenSpec specs:

### Реализовано
1. **Event Creation** — создание событий через /add с FSM воркфлоу
2. **Event Viewing** — просмотр событий через /today, /tomorrow, /week, /next_week, /all
3. **Event Deletion** — удаление событий через /del <id>
4. **Daily Summary** — ежедневная рассылка в 08:08 через APScheduler
5. **User Management** — регистрация через /start, настройки skip_empty
6. **Inline Calendar** — интерактивный календарь для выбора даты

### Архитектура
- Фреймворк: aiogram 3.x
- База данных: SQLAlchemy asyncio + SQLite (или PostgreSQL через DB_URL)
- Планировщик: APScheduler (daily_summary в 08:08)
- Состояния: aiogram FSM для воркфлоу создания событий
- Модель данных: User (telegram_id, settings_json) → Event (title, date_time, location)

## Impact
- Не требует изменений в коде
- Только документация текущего состояния

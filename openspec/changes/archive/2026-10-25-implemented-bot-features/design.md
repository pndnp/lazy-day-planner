# Design: Implemented Bot Features

## Context
Бот-напоминалка реализован как single Telegram bot с FSM воркфлоу для создания событий и APScheduler для ежедневных рассылок.

## Key Decisions

### FSM для создания событий
- Используется aiogram FSM для управления состояниями создания события
- Состояния: `waiting_for_title` → `waiting_for_date` → `waiting_for_time` → `waiting_for_location`
- Отмена через callback "cancel_new_event"

### Inline Calendar
- Генерация inline-календаря с callback data для каждой даты
- Навигация по месяцам через "calprev_" и "calnext_"
- Быстрый выбор "Сегодня" и "Завтра" через "calquick_"

### Хранение настроек
- Настройки пользователя хранятся как JSON в поле `settings_json`
- Методы: `get_setting`, `set_setting`, `toggle_setting`

### Daily Summary
- APScheduler запускает `daily_summary` ежедневно в 08:08
- Удаление прошедших событий при запуске
- Поддержка skip_empty для каждого пользователя

## Database Schema
```
users:
  - id: int (PK)
  - telegram_id: int (unique, index)
  - created_at: datetime
  - settings_json: string (JSON)

events:
  - id: int (PK)
  - title: string
  - date_time: datetime
  - location: string (nullable)
  - user_id: int (FK -> users.id)
```

## Files Structure
```
bot/
  config.py          # BOT_TOKEN, DB_PATH, TIMEZONE, DATE_FMT
  models.py          # User, Event models
  handlers/
    start.py         # /start, welcome
    add.py           # /add, FSM wizard, inline calendar
    view.py          # /today, /tomorrow, /week, /next_week, /all, /del
    settings.py      # /skipempty
  scheduler.py       # daily_summary
  main.py            # bot startup, router config
```

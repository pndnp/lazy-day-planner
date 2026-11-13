# Telegram‑бот «Напоминалка»

## Описание проекта

Бот напоминает о запланированных событиях на сегодня и завтра, а также позволяет просматривать план на текущую и следующую неделю. Поддерживается несколько пользователей – каждый пользователь хранит свои события в базе SQLite (можно переключить на PostgreSQL). В 08:08 каждый день бот отправляет пользователю сводный список событий на сегодня и завтра и удаляет прошедшие события.

## Технологический стек

- **Python 3.13+**
- **aiogram 3** – асинхронный клиент Telegram, FSM‑контекст для пошагового ввода.
- **SQLAlchemy [asyncio] + aiosqlite** – ORM‑слой, таблицы `User` и `Event`.
- **APScheduler (AsyncIOScheduler)** – планировщик задачи `daily_summary` (08:00).
- **SQLite** – локальное хранилище (можно заменить на PostgreSQL без изменения кода).

## Структура проекта

```
lazy-day/
│
├─ venv/                # виртуальное окружение (уже создано)
├─ .gitignore           # игнорируем __pycache__, venv, *.db, .env
├─ requirements.txt     # фиксированные версии зависимостей
├─ README.md            # текущий файл
│
├─ bot/                 # основной код
   ├─ __init__.py
   ├─ config.py        # BOT_TOKEN, DB_URL, TZ и пр.
   ├─ db.py            # async engine, Session factory
   ├─ models.py        # SQLAlchemy‑модели User & Event
   ├─ fsm.py           # состояния добавления события
   ├─ handlers/        # роутеры
   │   ├─ __init__.py
   │   ├─ start.py      # /start, /help
   │   ├─ add.py        # диалог /add
   └─ view.py       # /today, /tomorrow, /week, /next_week
   ├─ scheduler.py     # APScheduler‑задача daily_summary
    ├─ main.py          # создание Bot, Dispatcher, регистрация роутеров, запуск вебхука

```

## Как запустить локально (polling)

```bash
# активировать виртуальное окружение (если ещё не активировано)
source venv/bin/activate

# скопировать .env.example и заполнить BOT_TOKEN
cp .env.example .env

# установить зависимости (если ещё не установлены)
pip install -r requirements.txt

# запустить бота
python -m bot.main
```

Бот будет принимать команды:
- `/start` – приветствие и регистрация пользователя.
- `/add` – пошаговое добавление события (название → дата/время → место).
- `/today`, `/tomorrow`, `/week`, `/next_week` – просмотр планов.
- `/del <id>` – удаление события.
- `/help` – справка.

## Развёртывание с вебхуком

Для продакшена используется режим Telegram Webhook + Nginx для HTTPS.

### Требования

- Домен с направленным на сервер IP-адресом.
- Docker и Docker Compose.
- Сертификаты Let's Encrypt (автоматически получаются через certbot).

### Настройка

1. Скопируйте `.env.example` → `.env` и заполните:

```bash
cp .env.example .env
# Edit .env with your domain, certificate paths etc.
```

2. Замените `{{DOMAIN}}` в `nginx.conf` на ваш домен:

```bash
sed -i "s/{{DOMAIN}}/your-domain.com/g" nginx.conf
```

3. Поднимите сервисы:

```bash
docker compose up -d --build
```

### SSL-сертификаты

Let's Encrypt можно настроить вручную:

```bash
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  nginx:alpine \
  /bin/sh -c "apk add --no-cache certbot && certbot certonly --webroot --webroot-path=/var/www/certbot --email your-email@example.com -d your-domain.com"
```

Обновите пути к сертификатам в `.env`:

```
SSL_CERT_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem
```

## Расширение до многопользовательского режима

1. При первом `/start` проверяется запись в таблице `users`; если её нет – создаётся.
2. Все запросы к событиям фильтруются по `user_id = telegram_id`.
3. FSM‑контекст хранится в памяти (можно заменить на Redis при росте нагрузки).
4. При необходимости переключить СУБД – меняем `DB_URL` на `postgresql+asyncpg://user:pwd@host/db` и запускаем миграции.


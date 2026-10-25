# Proposal

## Why

Google OAuth requires an external HTTP endpoint for the callback. Currently it is served by a separate aiohttp server (`oauth_server.py:8080`) alongside the bot running in polling mode. For production deployment on VPS the bot must use Telegram Webhooks, which also require an HTTPS endpoint. Running two separate servers (one for Telegram polling, one for OAuth) is wasteful and complicates deployment.

## What Changes

- Replace `dp.start_polling(bot)` with `WebhookApplication(router).run_webhook()` pattern using aiogram's built-in webhook runner.
- Consolidate the OAuth callback server into the same aiohttp application that serves the Telegram webhook. One server, two routes:
  - `POST /webhook` — Telegram updates
  - `GET /oauth/callback` — Google OAuth 2.0 callback
- Require HTTPS for the webhook endpoint (required by Telegram). Document SSL certificate provisioning with Let's Encrypt/Certbot.
- Remove `bot/oauth_server.py` entirely — its callback handler moves to the consolidated aiohttp app.
- Remove polling from the codebase — no localhost fallback.

## Capabilities

### Modified Capabilities
- `user-management`: adding OAuth callback handling via the webhook endpoint instead of a separate server.

## Impact

- `bot/main.py` — replace polling with webhook setup using `aiogram.webhook`
- `bot/oauth_server.py` — **removed**, OAuth callback moves to new `bot/app_server.py` (or inline in main.py)
- `bot/config.py` — add `TELEGRAM_WEBHOOK_URL` (HTTPS URL)
- `bot/handlers/gcal.py` — update OAuth callback references
- `compose.yaml` — update Docker setup for webhook + HTTPS
- `README.md` — update deployment docs with webhook + SSL setup

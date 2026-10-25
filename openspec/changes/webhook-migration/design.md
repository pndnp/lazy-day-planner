# Design: Webhook Migration

## Problem
The bot currently runs in polling mode with a separate OAuth HTTP server on port 8080. This architecture is suitable for local development but not for production deployment where HTTPS webhook is required.

## Architecture Decision

### Single aiohttp Application
Instead of two separate servers (Telegram polling + OAuth server), use one aiohttp application:

```
┌─────────────────────────────────────────────┐
│  aiohttp.Server :80                         │
│                                             │
│  /webhook   → POST → Telegram updates       │
│  /oauth/    → GET  → Google OAuth callback  │
│  /health    → GET  → Health check           │
│                                             │
│  aiogram.webhook.WebhookApplication         │
│  └─ Dispatcher ──→ Bot handlers             │
└─────────────────────────────────────────────┘
        │
        ▼
   PostgreSQL/SQLite
   Telegram Bot API
   Google Calendar API
```

### Key Components

#### 1. Webhook Runner (main.py)
- Use `aiogram.webhook.WebhookApplication` to wrap the dispatcher router
- Set up aiohttp middleware for Telegram security headers
- Configure SSL context from `SSL_CERT_PATH` and `SSL_KEY_PATH`

#### 2. OAuth Callback Handler
- Move OAuth callback logic from `bot/oauth_server.py` to a new aiohttp route handler
- Path: `/oauth/callback` with query params `code`, `state`
- Use existing `oauth_flow.py` patterns for CSRF state management
- The `OAuthFlow` instance stores expected state in memory (sufficient for single-process deployment)

#### 3. SSL Termination
Two approaches:
- **Option A (recommended):** Nginx reverse proxy handles SSL, forwards plaintext to aiohttp on port 80
- **Option B:** aiohttp handles SSL directly using `ssl_context` from cert files

Recommended: Option A — Nginx is better at SSL termination, handles certificate renewal, and is standard practice.

#### 4. Environment Variables
```
TELEGRAM_WEBHOOK_URL=https://<domain>/webhook
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
OAUTH_CALLBACK_URL=https://<domain>/oauth/callback
```

## Files to Modify

### Created
- `bot/app_server.py` — unified aiohttp server configuration (webhook + OAuth routes)

### Modified
- `bot/main.py` — replace polling with webhook runner
- `bot/config.py` — add `TELEGRAM_WEBHOOK_URL`, `SSL_CERT_PATH`, `SSL_KEY_PATH`, `OAUTH_CALLBACK_URL`
- `bot/handlers/gcal.py` — update OAuth callback handling (remove `oauth_server` dependency)
- `compose.yaml` — update for webhook deployment (no separate OAuth container)

### Removed
- `bot/oauth_server.py` — functionality moved to unified server
- `bot/oauth_flow.py` — simplified (state management moves to app_server)

## Security Considerations

### Telegram Webhook Security
- Validate incoming Telegram requests using `X-Telegram-Bot-Api-Secret-Token` header
- Configure aiogram's security middleware with `WEBHOOK_SECRET_KEY` from env

### OAuth Security
- CSRF protection via `state` parameter (already implemented)
- Validate `state` in callback handler
- HTTPS only — no plaintext OAuth flows

### SSL/TLS
- Use TLS 1.2+
- Regular certificate renewal (Certbot)
- Strong cipher suites

## Docker Deployment

### compose.yaml structure
```yaml
services:
  bot:
    build: .
    ports:
      - "80:80"
    env_file: .env
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
```

### Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name <domain>;

    ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;

    location /webhook {
        proxy_pass http://bot:80/webhook;
        proxy_set_header Host $host;
    }

    location /oauth/ {
        proxy_pass http://bot:80/oauth/;
        proxy_set_header Host $host;
    }

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}

server {
    listen 80;
    server_name <domain>;
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    location / {
        return 301 https://$host$request_uri;
    }
}
```

## State Management

### OAuth State (in-memory)
The current `OAuthFlow` stores expected `state` values in memory (`Dict[str, asyncio.Event]`). This is sufficient for single-process deployment on a single VPS.

### Multi-process Warning
If the bot runs multiple workers (e.g., multiple Docker replicas), in-memory state will not work. For now, single process is acceptable.

## Rollback Plan

### If webhook migration fails
1. Revert Docker Compose deployment
2. Restore polling mode in `main.py`
3. Restore separate OAuth server
4. This migration is a one-time deploy — rollback means redeploying old code

### Testing before production
1. Test webhook on staging domain
2. Verify OAuth flow end-to-end with webhook URL
3. Test SSL certificate setup on staging VPS
4. Dry run on production VPS before switching domain DNS

## Timeline and Risk

### Risk: Nginx complexity
- **Mitigation:** Provide clear configuration template, use Certbot auto-renewal
- **Risk level:** Medium (well-documented process)

### Risk: OAuth state sync
- **Mitigation:** Single-process deployment, no concurrent OAuth flows per user
- **Risk level:** Low

### Risk: Telegram webhook timeout
- **Telegram allows 10s timeout for webhook responses**
- **Mitigation:** Long-running operations (GCAL API calls) handled asynchronously
- **Risk level:** Low

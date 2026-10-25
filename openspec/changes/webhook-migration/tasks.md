# Tasks: Webhook Migration

## Phase 1: Configuration

### Task 1.1: Add webhook configuration to `bot/config.py`
- [ ] Add `TELEGRAM_WEBHOOK_URL: str` — full HTTPS URL for webhook (e.g., `https://domain.com/webhook`)
- [ ] Add `SSL_CERT_PATH: str | None` — path to SSL certificate file
- [ ] Add `SSL_KEY_PATH: str | None` — path to SSL private key file
- [ ] Add `OAUTH_CALLBACK_URL: str | None` — OAuth callback URL derived from `TELEGRAM_WEBHOOK_URL`
- [ ] Keep `BOT_TOKEN` (required)

### Task 1.2: Update `compose.yaml` for webhook deployment
- [ ] Remove separate OAuth container
- [ ] Add `TELEGRAM_WEBHOOK_URL` env var
- [ ] Add volume mount for Let's Encrypt certificates
- [ ] Add Nginx service for HTTPS termination
- [ ] Expose port 443 for HTTPS
- [ ] Add port 80 redirect to HTTPS

## Phase 2: Unified HTTP server

### Task 2.1: Create `bot/app_server.py`
- [ ] Implement `_setup_webhook(app, bot, webhook_path)` — configure aiogram webhook middleware
- [ ] Implement `_setup_oauth_callback(app, callback_path, get_user_state)` — OAuth callback handler as aiohttp route
  - [ ] Parse `code` and `state` query params
  - [ ] Validate state against expected state
  - [ ] Store code in appropriate `asyncio.Event`
  - [ ] Return HTTP 200 with success message
- [ ] Implement `_setup_health_check(app)` — return 200 OK
- [ ] Implement `create_aiohttp_app(bot)` → `web.Application`
  - [ ] Register all routes
  - [ ] Set up CORS middleware (if needed)

### Task 2.2: Create state management helper for OAuth
- [ ] Implement `OAuthStateManager` class
  - [ ] `create_state() → str` — generate random state string
  - [ ] `wait_for_code(state: str, timeout: float = 300) → str` — await code for given state
  - [ ] `on_callback(state: str, code: str)` — store code when callback arrives
  - [ ] `cleanup()` — remove expired state entries
- [ ] State stored in memory (`dict[str, asyncio.Event]`)
- [ ] Thread-safe for single-process asyncio concurrency

## Phase 3: Replace polling with webhook

### Task 3.1: Modify `bot/main.py` — remove polling
- [ ] Remove `dp.start_polling(bot)`
- [ ] Import `create_aiohttp_app` from `bot.app_server`
- [ ] Create aiohttp app: `app = create_aiohttp_app(bot)`
- [ ] Set webhook URL with `await bot.set_webhook(TELEGRAM_WEBHOOK_URL)`
- [ ] Run webhook server with `WebhookApplication(app).run_webhook()`
  - [ ] Use host `0.0.0.0` for container/network listening
  - [ ] Use port 80
  - [ ] Conditionally enable SSL via `ssl_context` from `SSL_CERT_PATH`/`SSL_KEY_PATH`

### Task 3.2: Update OAuth URL references
- [ ] Modify `bot/config.py` — `get_redirect_uri()` should derive from `TELEGRAM_WEBHOOK_URL` + `/oauth/callback`
- [ ] Update any hardcoded `localhost:8080` URLs in the codebase
- [ ] Update `OAUTH_CALLBACK_DOMAIN` → use `OAUTH_CALLBACK_URL`

## Phase 4: Remove old OAuth server

### Task 4.1: Remove `bot/oauth_server.py`
- [ ] Delete the file — functionality moved to `app_server.py`
- [ ] Remove `get_oauth_server()` references from `main.py`
- [ ] Remove `oauth_srv` cleanup logic from `main.py`

### Task 4.2: Simplify `bot/oauth_flow.py`
- [ ] Remove standalone server startup logic
- [ ] Keep only the `OAuthFlow` class used by handlers
- [ ] Update callback URL to use `get_oauth_callback_url()` from config

### Task 4.3: Update `bot/handlers/gcal.py`
- [ ] Remove dependency on `bot.oauth_server`
- [ ] Use `OAuthFlow` from `bot.oauth_flow` directly
- [ ] Update auth URL building to use webhook domain

## Phase 5: Docker & deployment

### Task 5.1: Update `compose.yaml`
- [ ] Remove OAuth server container
- [ ] Update bot container env vars for webhook mode
- [ ] Add Nginx service for HTTPS termination
- [ ] Add Certbot volume for Let's Encrypt
- [ ] Configure Nginx to proxy `/webhook` and `/oauth/callback`

### Task 5.2: Create Nginx configuration template
- [ ] Create `nginx.conf` with webhook + OAuth proxy rules
- [ ] Include SSL configuration
- [ ] Include Let's Encrypt ACME challenge path
- [ ] Include HTTP → HTTPS redirect

### Task 5.3: Update `README.md`
- [ ] Document deployment steps for production
- [ ] Include Let's Encrypt setup (certbot)
- [ ] Include Nginx configuration example
- [ ] Include environment variables reference
- [ ] Remove polling mode documentation

### Task 5.4: Create `.env.production` example
- [ ] Add `.env.example` with webhook mode variables
- [ ] Document required values

## Phase 6: Testing & verification

### Task 6.1: Verify webhook registration
- [ ] Start bot → verify `set_webhook` succeeds
- [ ] Check `get_webhook_info` returns correct URL
- [ ] Send `/start` to bot → verify webhook update arrives

### Task 6.2: Verify OAuth flow with webhook URL
- [ ] Run with webhook mode configured
- [ ] Initiate Google Calendar OAuth from bot
- [ ] Auth callback should reach `/oauth/callback`
- [ ] Tokens should be stored correctly

### Task 6.3: SSL/HTTPS verification
- [ ] Verify SSL certificate is loaded
- [ ] Verify HTTPS connection works
- [ ] Verify Nginx proxy works end-to-end

### Task 6.4: Lint and type check
- [ ] `ruff check bot/` passes
- [ ] `mypy bot/` passes
- [ ] No imports of `bot.oauth_server` remain

### Task 6.5: Manual end-to-end test
- [ ] `/add` flow works with webhook
- [ ] "Add to Google Calendar" button works
- [ ] Daily summary at 08:08 works
- [ ] All existing commands work

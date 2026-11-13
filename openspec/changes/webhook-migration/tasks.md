# Tasks: Webhook Migration

## Phase 1: Configuration

### Task 1.1: Add webhook configuration to `bot/config.py`
- [x] Add `TELEGRAM_WEBHOOK_URL: str` — full HTTPS URL for webhook (e.g., `https://domain.com/webhook`)
- [x] Add `SSL_CERT_PATH: str | None` — path to SSL certificate file
- [x] Add `SSL_KEY_PATH: str | None` — path to SSL private key file
- [ ] Add `OAUTH_CALLBACK_URL: str | None` — OAuth callback URL derived from `TELEGRAM_WEBHOOK_URL` (OAuth not implemented)
- [x] Keep `BOT_TOKEN` (required)

### Task 1.2: Update `compose.yaml` for webhook deployment
- [x] Remove separate OAuth container
- [x] Add `TELEGRAM_WEBHOOK_URL` env var
- [x] Add volume mount for Let's Encrypt certificates
- [x] Add Nginx service for HTTPS termination
- [x] Expose port 443 for HTTPS
- [x] Add port 80 redirect to HTTPS

## Phase 2: Unified HTTP server

### Task 2.1: Create `bot/app_server.py`
- [x] Implement `_setup_health_check(app)` — return 200 OK
- [x] Implement `create_aiohttp_app(bot, dp)` → `web.Application`
  - [x] Register all routes (/health only; /oauth/callback commented out per user request)
  - [x] Set up security headers middleware

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
- [x] Remove `dp.start_polling(bot)`
- [x] Import `create_aiohttp_app` from `bot.app_server`
- [x] Create aiohttp app: `app = create_aiohttp_app(bot, dp)`
- [x] Set webhook URL with `await bot.set_webhook(TELEGRAM_WEBHOOK_URL)`
- [x] Run webhook server with SimpleRequestHandler + setup_application
  - [x] Use host `0.0.0.0` for container/network listening
  - [x] Use port 80
  - [x] Conditionally enable SSL via `ssl_context` from `SSL_CERT_PATH`/`SSL_KEY_PATH`

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
- [x] Remove OAuth server container
- [x] Update bot container env vars for webhook mode
- [x] Add Nginx service for HTTPS termination
- [x] Add Certbot volume for Let's Encrypt
- [x] Configure Nginx to proxy `/webhook` (`/oauth/callback` commented out per user request)

### Task 5.2: Create Nginx configuration template
- [x] Create `nginx.conf` with webhook proxy rules (`/oauth/callback` commented out per user request)
- [x] Include SSL configuration
- [x] Include Let's Encrypt ACME challenge path
- [x] Include HTTP → HTTPS redirect

### Task 5.3: Update `README.md`
- [x] Document deployment steps for production
- [x] Include Let's Encrypt setup (certbot)
- [x] Include Nginx configuration example
- [x] Include environment variables reference
- [x] Keep local polling development instructions for convenience

### Task 5.4: Create `.env.example`
- [x] Add `.env.example` with webhook mode variables
- [x] Document required values

## Phase 6: Testing & verification

### Task 6.1: Verify webhook registration
<!-- TODO: Test manually with real Telegram bot token and public domain -->

### Task 6.2: Verify OAuth flow with webhook URL
- [ ] Run with webhook mode configured
- [ ] Initiate Google Calendar OAuth from bot
- [ ] Auth callback should reach `/oauth/callback`
- [ ] Tokens should be stored correctly

### Task 6.3: SSL/HTTPS verification
<!-- TODO: Test with real certificates via certbot or self-signed -->

### Task 6.4: Lint and type check
- [x] `ruff check bot/main.py bot/app_server.py` passes
- [ ] `mypy bot/` passes (pre-existing errors in handlers/scheduler, not introduced by this PR)
- [x] No imports of `bot.oauth_server` remain

### Task 6.5: Manual end-to-end test
<!-- TODO: Deploy and test /add flow, daily summary, all commands -->

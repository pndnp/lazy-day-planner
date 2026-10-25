# Spec Delta: Webhook Migration

## Purpose
Migrate the Telegram bot from polling mode to webhook mode and consolidate the OAuth callback HTTP server into the same aiohttp application, eliminating the need for a separate port and enabling production deployment on VPS with HTTPS.

## ADDED Requirements

### Requirement: Webhook server with aiogram
The application must use Telegram Bot API webhook instead of polling, configured via aiogram's `WebhookApplication` router.

#### Scenario: Webhook application setup
- **WHEN** the application starts
- **THEN** it uses `aiogram.webhook.WebhookApplication` wrapping the dispatcher router
- **AND** the webhook runs on a single aiohttp server listening on port 80
- **AND** the webhook path is configurable (default: `/webhook`)

#### Scenario: Polling mode removed
- **WHEN** the application runs
- **THEN** it never calls `dp.start_polling(bot)`
- **AND** there is no polling fallback in the code

### Requirement: Unified HTTP server with OAuth callback
The aiohttp server that handles the Telegram webhook must also serve the Google OAuth 2.0 callback.

#### Scenario: OAuth callback on same server
- **WHEN** Google redirects to the OAuth callback URL
- **THEN** the request is handled by the same aiohttp server that serves the Telegram webhook
- **AND** the OAuth callback uses path `/oauth/callback` distinct from `/webhook`

#### Scenario: Request routing by path
- **WHEN** a request arrives at `/webhook`
- **THEN** it is processed as a Telegram update (POST request)
- **WHEN** a request arrives at `/oauth/callback`
- **THEN** it is processed as an OAuth callback (GET request with query params)

#### Scenario: OAuth flow without separate server
- **WHEN** a user initiates Google Calendar OAuth
- **THEN** the auth URL uses the webhook domain instead of `localhost:8080`
- **AND** after OAuth, the callback reaches the same aiohttp server
- **AND** the OAuth server instance is no longer needed as a separate component

### Requirement: HTTPS configuration
The webhook endpoint must use HTTPS as required by Telegram Bot API.

#### Scenario: HTTPS enforced for webhook
- **WHEN** the webhook runs in production
- **THEN** the webhook URL is configured with HTTPS scheme
- **AND** SSL certificate path is configurable via environment variable

#### Scenario: SSL certificate setup
- **WHEN** deployment documentation is read
- **THEN** it includes instructions for Let's Encrypt/Certbot setup
- **AND** it covers Nginx reverse proxy configuration for SSL termination
- **AND** it covers automatic certificate renewal

### Requirement: Configuration variables
The application must use environment variables for webhook and SSL configuration.

#### Scenario: Webhook URL configuration
- **WHEN** the application reads config
- **THEN** it reads `TELEGRAM_WEBHOOK_URL` — the full HTTPS URL for the webhook endpoint
- **AND** it reads `SSL_CERT_PATH` and `SSL_KEY_PATH` for SSL certificate files
- **AND** `TELEGRAM_WEBHOOK_URL` is required when running in production

### Requirement: OAuth server removal
The separate `oauth_server.py` module must be removed as its functionality is consolidated.

#### Scenario: Consolidated OAuth handling
- **WHEN** an OAuth callback arrives at `/oauth/callback`
- **THEN** it is handled by a route handler in the aiohttp application
- **AND** the same state management (asyncio.Event, state tokens) is preserved
- **AND** `bot/oauth_server.py` no longer exists

## MODIFIED Requirements

### Requirement: user-management capability
- **WHEN** the OAuth callback is handled via webhook
- **THEN** the user management spec remains unchanged (OAuth still stores tokens and emails in user settings)

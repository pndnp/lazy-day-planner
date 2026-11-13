"""Unified aiohttp server for Telegram webhook and health checks."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiohttp import web


def create_aiohttp_app(bot: Any, dp: Any) -> web.Application:
    """Create and configure the aiohttp application.

    Registers health check route and security headers middleware.
    The Telegram webhook handler is registered by :func:`main.main`.

    Args:
        bot: The aiogram Bot instance (stored on the app so handlers can reach it).
        dp: The aiogram Dispatcher instance (unused here but kept for consistency).

    Returns:
        Configured aiohttp ``web.Application`` instance.
    """
    app = web.Application()
    app["bot"] = bot

    # Health check endpoint
    app.router.add_get("/health", _health_handler)

    # OAuth callback placeholder (not yet implemented)
    # app.router.add_get("/oauth/callback", _health_handler)

    # Middleware: add security headers to all responses
    @web.middleware  # type: ignore
    async def security_middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
    ) -> web.StreamResponse:
        resp = await handler(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        return resp

    app.middlewares.append(security_middleware)
    return app


async def _health_handler(request: web.Request) -> web.Response:
    """Simple health-check endpoint returning 200 OK."""
    return web.Response(status=200, text="OK")

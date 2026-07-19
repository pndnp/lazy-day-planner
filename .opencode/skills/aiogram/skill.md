---
name: aiogram
description: Telegram bots using aiogram 3.x.
---

# aiogram 3.x

Use latest aiogram 3.x APIs.

## Project layout

Prefer:

handlers/
services/
keyboards/
middlewares/
filters/
states/

## Handlers

Handlers should only:

- validate input
- call service
- send response

Business logic never belongs inside handlers.

## FSM

FSM stores conversation state only.

Do not put business logic into FSM.

## Dependency Injection

Inject services.

Avoid global variables.

## Keyboards

Keep keyboard generation separate.

Never generate keyboards inside handlers.

## CallbackData

Prefer typed CallbackData.

Avoid parsing callback strings manually.

## Bot API

Prefer built-in aiogram methods.

Avoid raw HTTP requests.

## Messages

Keep messages localized.

Avoid hardcoded text throughout handlers.

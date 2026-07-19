---
name: architecture
description: Clean Architecture for Python backend projects.
---

# Layers

UI

↓

Application Services

↓

Repositories

↓

Infrastructure

Business logic must not depend on Telegram or database.

## Dependencies

Allowed:

Handler

↓

Service

↓

Repository

Forbidden:

Repository -> Handler

Handler -> Database

## Services

Services contain business logic.

Repositories only persist data.

## Repositories

Repositories know SQL.

Services never do.

## Dependency Injection

Inject dependencies.

Avoid global singletons.

## Configuration

Configuration comes from pydantic-settings.

Never hardcode:

- URLs
- tokens
- secrets

## Modules

Prefer many small modules over huge files.

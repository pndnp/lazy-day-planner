---
name: project-conventions
description: Conventions for this Telegram reminder bot project.
---

# Stack

Python 3.12

uv

aiogram 3.x

pytest

ruff

mypy

pydantic-settings

## Commands

Run:

uv run ...

Install:

uv sync

Tests:

uv run pytest

Lint:

uv run ruff check

Format:

uv run ruff format

Types:

uv run mypy

## Code generation

When adding new feature:

1. explain architecture

2. describe affected modules

3. implement

4. suggest tests

## Never

Never modify unrelated files.

Never rename public APIs without explanation.

Never introduce unnecessary dependencies.

## Responses

Explain architectural decisions briefly.

Highlight trade-offs.

Keep code simple.

Prefer maintainability.

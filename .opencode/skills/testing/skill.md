---
name: testing
description: Testing Python applications with pytest.
---

# Framework

Use pytest.

## Test

Business logic.

Edge cases.

Failure scenarios.

## Avoid

Testing framework internals.

Testing trivial getters.

## Fixtures

Prefer fixtures over duplicated setup.

## Mock

Mock:

- Telegram API
- HTTP
- database
- external services

## Naming

test_create_user_success

test_invalid_token

test_duplicate_reminder

## Assertions

One logical scenario per test.

Prefer explicit assertions.

## Refactoring

When changing business logic:

Suggest tests first.

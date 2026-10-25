# Proposal

## Why

Users have no way to remove their data from the bot. Since the bot stores Telegram ID, event data, and Google Calendar tokens, providing a way to delete all user data is necessary for privacy compliance and user trust.

## What Changes

- Add `/deleteaccount` command that initiates a multi-step deletion flow:
  1. Bot sends a message listing what will be deleted (all events, Google tokens, settings) and what will NOT be deleted (Google Calendar events that were synced remain in the user's calendar).
  2. Bot waits for confirmation — inline keyboard with "Удалить аккаунт" / "Отмена".
  3. On confirmation: delete all `Event` records and the `User` record from the database.
  4. Send a success message: "Аккаунт удалён. Все данные успешно удалены. События в вашем Google Календаре остались без изменений."
- On cancellation: inform the user the account was not deleted, no changes made.

## Capabilities

### New Capabilities
None — this extends existing capability.

### Modified Capabilities
- `user-management`: adding a new requirement for account deletion (data removal by user request).

## Impact

- `bot/handlers/start.py` — add `/deleteaccount` handler
- `bot/models.py` — User deletion (cascade already handles Event removal, but explicit deletion is preferred)
- `bot/main.py` — register new command in `BotCommand` list
- `bot/fsm.py` — may need a new FSM state for the confirmation flow
- New spec delta for `user-management` capability
- New integration/confirmation flow in the handlers

# Design: Account Deletion

## Problem
Users need to be able to delete their account and all associated data from the bot on request. This is required for privacy compliance (GDPR, etc.).

## Data Deletion Strategy

### What gets deleted
- `User` record from `users` table (cascade deletes all `Event` records)
- Google Calendar tokens stored in `User.settings` (as JSON)
- All `Event` records in the database

### What does NOT get deleted
- Google Calendar events that were synced — these live in the user's Google account, not the bot's database. Deleting them would require:
  - The `gcal_event_id` stored per event
  - Additional GCAL API calls
  - User consent for each deletion
  - Risk of data loss (user may have added events manually in GCAL)
  - **Decision:** Inform the user, but do NOT delete GCAL events.

### Deletion cascade
Since `Event` has `ForeignKey('users.id', cascade='all, delete-orphan')`, deleting the `User` automatically deletes associated events in SQLAlchemy.

## Implementation Approach

### FSM-based confirmation flow
The `/deleteaccount` command uses a multi-step interaction:

```
User: /deleteaccount
Bot:  "Будет удалено: [list]
       Не будет удалено: [GCAL events]

       [Удалить аккаунт] [Отмена]"

User: clicks "Удалить аккаунт"
Bot:  "Аккаунт удалён..."
```

No FSM state is needed — the inline keyboard response is handled directly in the callback handler.

### Handler structure

#### `bot/handlers/start.py` (new handler)
- `@dp.message(delete_account_cmd)` — initiates the flow
- Sends deletion confirmation message with inline keyboard

#### `bot/handlers/start.py` (callback handler)
- `@dp.callback_query(F.data == "delete_account_confirm")` — processes deletion
- `@dp.callback_query(F.data == "delete_account_cancel")` — cancels deletion
- Uses SQLAlchemy session to:
  1. Query events for the user (for logging)
  2. Delete events
  3. Delete user

### Database deletion

```python
# Example deletion logic:
async def _delete_user_events(session, user):
    events = await session.execute(
        select(Event).where(Event.user_id == user.id)
    )
    for event in events.scalars().all():
        await session.delete(event)

    await session.delete(user)
    await session.commit()
```

Or simpler (cascade):
```python
async with session() as s:
    user = await s.get(User, user_id)
    if user:
        await s.delete(user)
        await s.commit()
```

### Security considerations
- **One-time confirmation:** Deletion is irreversible. The inline keyboard requires explicit confirmation.
- **No accidental deletion:** Two-step flow (initiate → confirm) prevents accidental deletion via accidental command send.
- **No rollback:** Once deleted, data cannot be recovered.

### Edge cases
- **User sends `/deleteaccount` while in wizard flow:** The command handler should take precedence (clear FSM first, per `ClearFSMOnCommandMiddleware`).
- **User already deleted:** If user doesn't exist, send "User not found" (shouldn't happen if user accessed bot).
- **Google OAuth tokens:** These are stored in the User settings — they are deleted along with the user.

## Files to Modify

### Modified
- `bot/handlers/start.py` — add `/deleteaccount` handler and callback handlers
- `bot/main.py` — add `/deleteaccount` to `BotCommand` list

### Not modified
- `bot/models.py` — User model already has cascade delete for events
- `bot/config.py` — no config changes needed
- `bot/fsm.py` — no new FSM state needed (inline keyboard is stateless)

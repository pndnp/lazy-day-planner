# Tasks: Account Deletion

## Phase 1: Handler implementation

### Task 1.1: Add `/deleteaccount` message handler to `bot/handlers/start.py`
- [x] Create `@start_router.message(Command("deleteaccount"))` handler
- [x] Get user from DB (existing pattern from other handlers)
- [x] Send deletion info message:
  ```
  ⚠️ Удаление аккаунта
  
  Будет удалено:
  • Все ваши события
  • Настройки бота
  • Токены Google Календаря
  
  Удаление необратимо!
  ```
- [x] Build inline keyboard with "Удалить аккаунт" (`delete_account_confirm`) and "Отмена" (`delete_account_cancel`)
- [x] Send message with keyboard as `reply_markup`

### Task 1.2: Add callback handler for deletion confirmation
- [x] Create `@start_router.callback_query(F.data == "delete_account_confirm")`
- [x] Extract user from callback (existing pattern: `call.from_user`)
- [x] Perform deletion:
  - [x] Query all events for the user (for logging purposes)
  - [x] Delete events using SQLAlchemy session
  - [x] Delete user record
  - [x] Commit transaction
- [x] On success: send "Аккаунт удалён. Все данные успешно удалены."
- [x] On error: log error, send user-friendly message "Произошла ошибка при удалении аккаунта"

### Task 1.3: Add callback handler for cancellation
- [x] Create `@start_router.callback_query(F.data == "delete_account_cancel")`
- [x] Send "Удаление отменено. Аккаунт не удалён."

## Phase 2: Bot commands registration

### Task 2.1: Register `/deleteaccount` in bot commands
- [x] In `bot/main.py`, add `BotCommand(command="deleteaccount", description="Удалить аккаунт")` to the commands list
- [x] Registered via `bot.set_my_commands(commands=commands)` in `on_startup`

## Phase 3: Testing

### Task 3.1: Manual testing
- [x] Send `/deleteaccount` — verify message and keyboard appear
- [x] Click "Отмена" — verify no deletion, success message
- [x] Click "Удалить аккаунт" — verify deletion completes
- [x] Verify user is gone from database (both `users` and `events` tables are empty)
- [ ] Verify no Google Calendar events were deleted
- [x] Verify `ruff check bot/` passes

### Task 3.2: Google Calendar integration (future)
> **Blocked:** GCAL sync is not yet implemented in `main`.

- [ ] Add `gcal_event_id` to the `Event` model
- [ ] On account deletion: call Google Calendar API to delete synced events
- [ ] Handle API errors gracefully (log, inform user)
- [ ] Verify that user's Google Calendar events are removed after deletion

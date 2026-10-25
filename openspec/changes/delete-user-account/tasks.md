# Tasks: Account Deletion

## Phase 1: Handler implementation

### Task 1.1: Add `/deleteaccount` message handler to `bot/handlers/start.py`
- [ ] Create `@dp.message(F.command == "delete_account")` handler
- [ ] Get user from DB (existing pattern from other handlers)
- [ ] Send deletion info message:
  ```
  ⚠️ Удаление аккаунта
  
  Будет удалено:
  • Все ваши события
  • Настройки бота
  • Токены Google Календаря
  
  НЕ будет удалено:
  • События в вашем Google Календаре (останутся без изменений)
  
  Удаление необратимо!
  ```
- [ ] Build inline keyboard with "Удалить аккаунт" (`delete_account_confirm`) and "Отмена" (`delete_account_cancel`)
- [ ] Send message with keyboard as `reply_markup`

### Task 1.2: Add callback handler for deletion confirmation
- [ ] Create `@dp.callback_query(F.data == "delete_account_confirm")`
- [ ] Extract user from callback (existing pattern: `call.from_user`)
- [ ] Perform deletion:
  - [ ] Query all events for the user (for logging purposes)
  - [ ] Delete events using SQLAlchemy session
  - [ ] Delete user record
  - [ ] Commit transaction
- [ ] On success: send "Аккаунт удалён. Все данные успешно удалены. События в вашем Google Календаре остались без изменений."
- [ ] On error: log error, send user-friendly message "Произошла ошибка при удалении аккаунта"

### Task 1.3: Add callback handler for cancellation
- [ ] Create `@dp.callback_query(F.data == "delete_account_cancel")`
- [ ] Send "Удаление отменено. Аккаунт не удалён."

## Phase 2: Bot commands registration

### Task 2.1: Register `/deleteaccount` in bot commands
- [ ] In `bot/main.py`, add `BotCommand(command="deleteaccount", description="Удалить аккаунт")` to the commands list

## Phase 3: Testing

### Task 3.1: Manual testing
- [ ] Send `/deleteaccount` — verify message and keyboard appear
- [ ] Click "Отмена" — verify no deletion, success message
- [ ] Click "Удалить аккаунт" — verify deletion completes
- [ ] Verify user is gone from database
- [ ] Verify no Google Calendar events were deleted
- [ ] Verify `ruff check bot/` passes

# Spec Delta: Account Deletion

## MODIFIED Requirements

### Requirement: Account deletion via `/deleteaccount` command
The bot must allow users to permanently delete their account and all associated data from the bot.

#### Scenario: User initiates account deletion
- **WHEN** user sends `/deleteaccount` command
- **THEN** bot sends a message listing what will be deleted (all events, Google tokens, settings)
- **AND** bot presents an inline keyboard with "Удалить аккаунт" and "Отмена" buttons
- **TODO (GCAL sync not yet implemented):** Do NOT include information about Google Calendar events remaining, as GCAL sync functionality is not yet in main. Once GCAL sync is implemented, add: and what will NOT be deleted (Google Calendar events that were synced)

#### Scenario: User confirms account deletion
- **WHEN** user clicks "Удалить аккаунт" button
- **THEN** bot deletes all `Event` records belonging to the user
- **AND** bot deletes the `User` record from the database
- **AND** bot sends success message: "Аккаунт удалён. Все данные успешно удалены."
- **TODO (GCAL sync not yet implemented):** Do NOT include "События в вашем Google Календаре остались без изменений." in the success message. Once GCAL sync is implemented, add this note back.

#### Scenario: User cancels account deletion
- **WHEN** user clicks "Отмена" button
- **THEN** bot informs the user the account was not deleted
- **AND** no changes are made to the database

#### Scenario: Delete account with Google Calendar events
- **TODO (GCAL sync not yet implemented):** This scenario is blocked until GCAL sync is implemented.
- **WHEN** user has Google Calendar events synced (future feature)
- **THEN** bot explicitly informs that Google Calendar events remain in the user's calendar
- **AND** only the bot-side records (User, Event, tokens) are deleted

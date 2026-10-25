# inline-calendar Specification

## Purpose
Предоставляет интерактивный календарь для выбора даты события через inline-кнопки Telegram.

## Requirements

### Requirement: Calendar Keyboard Generation
Система должна генерировать inline-календарь для выбора даты.

#### Scenario: Generate calendar for current month
- **Given** система показывает календарь
- **WHEN** система генерирует клавиатуру
- **THEN** календарь отображает текущий месяц с днями недели
- **AND** каждая дата — это кнопка с callback data "caldate_YYYY-MM-DD"
- **AND** пустые ячейки имеют callback data "calignore"

#### Scenario: Calendar navigation buttons
- **Given** календарь отображается
- **WHEN** система добавляет навигацию
- **THEN** есть кнопка "←" с callback data "calprev_YYYY-MM" для предыдущего месяца
- **AND** есть кнопка "→" с callback data "calnext_YYYY-MM" для следующего месяца

### Requirement: Quick Date Selection
Система должна предоставлять быстрые кнопки для выбора today и tomorrow.

#### Scenario: Today quick button
- **Given** календарь отображается
- **AND** пользователь нажимает "Сегодня"
- **WHEN** система обрабатывает callback
- **THEN** система сохраняет сегодняшнюю дату и переходит к вводу времени

#### Scenario: Tomorrow quick button
- **Given** календарь отображается
- **AND** пользователь нажимает "Завтра"
- **WHEN** система обрабатывает callback
- **THEN** система сохраняет завтрашнюю дату и переходит к вводу времени

### Requirement: Calendar State Management
Система должна управлять состоянием inline календаря.

#### Scenario: Handle calendar button clicks
- **Given** пользователь видит календарь
- **AND** пользователь нажимает на пустую ячейку
- **WHEN** система обрабатывает callback "calignore"
- **THEN** система не выполняет никаких действий и показывает "Answer callback"

#### Scenario: Edit calendar month
- **Given** пользователь видит календарь
- **AND** пользователь нажимает "←" или "→"
- **WHEN** система обрабатывает callback "calprev_" или "calnext_"
- **THEN** система редактирует сообщение с новым календарём

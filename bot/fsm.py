from aiogram.fsm.state import State, StatesGroup


class NewEventState(StatesGroup):
    waiting_for_title = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_location = State()

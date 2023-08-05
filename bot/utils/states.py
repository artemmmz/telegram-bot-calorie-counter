from aiogram.dispatcher.filters.state import StatesGroup, State


class CalculateState(StatesGroup):
    for_what = State()
    gender = State()
    age = State()
    growth = State()
    weight = State()
    activity = State()
    waiting_for_finish = State()

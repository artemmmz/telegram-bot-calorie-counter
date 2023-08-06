from aiogram.dispatcher.filters.state import StatesGroup, State


class SettingsState(StatesGroup):
    language = State()
    mass_unit = State()
    time_zone = State()


class CalculateState(StatesGroup):
    for_what = State()
    gender = State()
    age = State()
    growth = State()
    weight = State()
    activity = State()
    waiting_for_finish = State()


class RecordState(StatesGroup):
    weight = State()
    protein = State()
    fat = State()
    carb = State()

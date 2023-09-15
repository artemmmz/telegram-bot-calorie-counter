from datetime import datetime
from math import ceil

from aiogram import Dispatcher, filters, types, exceptions
from aiogram.dispatcher import FSMContext

from config import TELEGRAM_BOT_SUPERUSER_ID
from db import Database
from db.structures import create_user, create_record
from db.utils import get_user, get_user_unit
from keyboards import (
    get_gender_inline_keyboard,
    get_menu_inline_keyboard,
    get_calculate_finish_inline_keyboard,
    get_unit_inline_keyboard,
    get_settings_end_inline_keyboard,
    get_settings_inline_keyboard,
    get_keyboard_of_nums,
    get_timezone_keyboard,
    get_statistics_keyboard,
    get_records_keyboard,
)
from utils.consts import RECORDS_PAGE_NUM, MASS_UNITS, PER_MASS_TEXTS
from utils.states import CalculateState, RecordState, SettingsState, LimitState
from utils.texts import gettext, Text, Word
from utils.utils import kcal_limit, limits, ounce_to_gram, gram_to_ounce

db_users = Database('users')
_ = gettext


# COMMANDS
async def command_start(message: types.Message):
    await message.answer(
        Text.HELLO.format(t=Text.UNIT),
        reply_markup=get_unit_inline_keyboard(),
    )
    await SettingsState.mass_unit.set()
    user_id = message.from_user.id
    db_users.add_records(
        create_user(
            user_id=user_id,
            is_admin=user_id == TELEGRAM_BOT_SUPERUSER_ID,
            is_superuser=user_id == TELEGRAM_BOT_SUPERUSER_ID,
        )
    )


async def command_menu(message: types.Message):
    await message.answer(
        Text.MENU,
        parse_mode='HTML',
        reply_markup=get_menu_inline_keyboard(),
    )


async def command_statistics(
    message: types.Message, date_string: str | None = None
):
    edit_message = True
    if date_string is None:
        date_string = 'today'
        edit_message = False
    user_id = message.from_user.id
    user = get_user(user_id, date_string)
    date_string = user['date_str']

    unit = _(user['settings']['unit'])

    text = Text.STATISTICS.format(
        u=unit,
        s=user['statistics'],
        l=user['limits'],
    )
    reply_markup = get_statistics_keyboard(date_string, user['today_str'])

    if edit_message:
        await message.edit_text(text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)


async def command_records(
    message: types.Message,
    date_string: str | None = None,
    page: int | None = None,
):
    user_id = message.from_user.id
    edit_message = True
    if date_string is None:
        date_string = 'today'
        edit_message = False
    if page is None:
        page = 0
    user = get_user(user_id, date_string)
    unit = _(user['settings']['unit'])

    date_string = user['date_str']
    records_date = user['records_date']
    records_date_page = records_date[
        page * RECORDS_PAGE_NUM: (page + 1) * RECORDS_PAGE_NUM  # fmt: skip
    ]
    records = [
        Text.RECORD.format(r=record, unit=unit) for record in records_date_page
    ]

    records_text = (
        '\n'.join(records) if len(records) > 0 else Word.EMPTY.capitalize()
    )
    text = Text.RECORDS.format(rt=records_text)
    reply_markup = get_records_keyboard(
        date_string,
        user['today_str'],
        page,
        ceil(len(records_date) / RECORDS_PAGE_NUM),
    )

    if edit_message:
        await message.edit_text(text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)


async def command_settings(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    unit = MASS_UNITS[user['settings']['unit']][0]
    user['settings']['unit'] = MASS_UNITS[user['settings']['unit']][1]

    text = Text.SETTINGS.format(
        s=user['settings'],
        l=user['limits'],
        u=unit,
    )

    await message.answer(text, reply_markup=get_settings_inline_keyboard())


async def command_setting(message: types.Message, setting: str | None = None):
    ANSWERS = {
        'timezone': (Text.TIMEZONE, get_timezone_keyboard()),
        'unit': (Text.UNIT, get_unit_inline_keyboard()),
    }
    await message.answer(ANSWERS[setting][0], reply_markup=ANSWERS[setting][1])


async def command_setting_edit(
    message: types.Message,
    setting: str | None = None,
    value: str | None = None,
):
    db_users.update_elem(
        {'user_id': message.from_user.id},
        {f'settings.{setting}': value},
    )
    await command_settings(message)


async def command_limit(
    message: types.Message, state: FSMContext, name: str | None = None
):
    await LimitState.edit.set()
    await state.update_data({'name': name})
    ANSWERS = {
        'protein': Text.INPUT_LIMIT_PROTEIN,
        'fat': Text.INPUT_LIMIT_FAT,
        'carb': Text.INPUT_LIMIT_CARB,
    }
    await message.answer(ANSWERS[name])


async def command_limit_edit(message: types.Message, state: FSMContext):
    try:
        answer = message.text.replace(',', '.')
        value = float(answer)
    except ValueError:
        await message.answer(Text.NUMBER)
        return
    user_id = message.from_user.id
    name = (await state.get_data())['name']
    await state.finish()
    unit = get_user_unit(user_id)
    if unit == 'oz':
        value = ounce_to_gram(value)
    db_users.update_elem({'user_id': user_id}, {f'limits.{name}': value})
    await command_settings(message)


async def command_cancel(message: types.Message, state: FSMContext):
    if await state.get_state():
        await state.finish()
        await command_menu(message)


# CALLBACKS
async def callback_open_menu(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.delete()
    except exceptions.MessageCantBeDeleted:
        ...
    await command_menu(callback_query.message)


async def callback_statistics(callback_query: types.CallbackQuery):
    date_string = callback_query.data[len('statistics_'):]  # fmt: skip
    if date_string == '':
        await callback_query.message.delete()
        date_string = None
    callback_query.message.from_user = callback_query.from_user
    await command_statistics(callback_query.message, date_string)


async def callback_records(callback_query: types.CallbackQuery):
    params_raw = callback_query.data[len('records_'):]  # fmt: skip
    if params_raw == '':
        await callback_query.message.delete()
        date_string, page = None, None
    else:
        params = params_raw.split('_')
        date_string = params[0]
        page = int(params[1][len('p'):])  # fmt: skip
    callback_query.message.from_user = callback_query.from_user
    try:
        await command_records(callback_query.message, date_string, page)
    except exceptions.MessageNotModified:
        await callback_query.answer(Word.ERROR.capitalize(), show_alert=True)


async def callback_settings(callback_query: types.CallbackQuery):
    callback_query.message.from_user = callback_query.from_user
    try:
        await callback_query.message.delete()
    except exceptions.MessageCantBeDeleted:
        ...
    await command_settings(callback_query.message)


async def callback_setting(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.delete()
    except exceptions.MessageCantBeDeleted:
        ...
    callback_query.message.from_user = callback_query.from_user
    params = callback_query.data.split('_')
    setting = params[1]
    await command_setting(callback_query.message, setting)


async def callback_setting_edit(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.delete()
    except exceptions.MessageCantBeDeleted:
        ...
    callback_query.message.from_user = callback_query.from_user
    params = callback_query.data.split('_')
    setting = params[1]
    value = params[2]
    await command_setting_edit(callback_query.message, setting, value)


async def callback_limit(
    callback_query: types.CallbackQuery, state: FSMContext
):
    try:
        await callback_query.message.delete()
    except exceptions.MessageCantBeDeleted:
        ...
    callback_query.message.from_user = callback_query.from_user
    params = callback_query.data.split('_')
    name = params[1]
    await command_limit(callback_query.message, state, name)


async def callback_cancel(
    callback_query: types.CallbackQuery, state: FSMContext
):
    try:
        await callback_query.message.delete()
    except exceptions.MessageCantBeDeleted:
        ...
    await command_cancel(callback_query.message, state)


# STATES
# Settings state
async def settings_state_unit(
    callback_query: types.CallbackQuery,
    state: FSMContext,
) -> None:
    await callback_query.message.delete()
    answer = callback_query.data[len('settings_unit_'):]  # fmt: skip
    await state.update_data({'unit': answer})
    await SettingsState.next()

    await command_setting(callback_query.message, 'unit')


async def settings_timezone_page(callback_query: types.CallbackQuery):
    page = int(callback_query.data[len('settings_zone_page_'):])  # fmt: skip
    await callback_query.message.edit_reply_markup(get_timezone_keyboard(page))


async def settings_state_timezone(
    callback_query: types.CallbackQuery, state: FSMContext
):
    await callback_query.message.delete()
    answer = callback_query.data[len('settings_zone_'):]  # fmt: skip
    await state.update_data({'timezone': answer})

    data = await state.get_data()
    db_users.update_elem(
        {'user_id': callback_query.from_user.id}, {'settings': data}
    )
    await state.finish()

    await callback_query.message.answer(
        Text.SETTINGS_END,
        reply_markup=get_settings_end_inline_keyboard(),
    )


# Calculate State
async def command_calculate_calories(
    message: types.Message, state: FSMContext
):
    await CalculateState.for_what.set()
    unit = db_users.get_record(
        {'user_id': message.from_user.id}, {'settings.unit': 1}
    )['settings']['unit']
    await state.update_data({'unit': unit})
    await message.answer(
        Text.FOR_WHAT,
        reply_markup=get_keyboard_of_nums(3, prefix='for_what'),
    )


async def callback_calculate_calories(
    callback_query: types.CallbackQuery, state: FSMContext
):
    await callback_query.message.delete()
    callback_query.message.from_user = callback_query.from_user
    await command_calculate_calories(callback_query.message, state)


async def calculate_state_for_what(
    callback_query: types.CallbackQuery, state: FSMContext
):
    ind = int(callback_query.data[len('for_what_'):])  # fmt: skip
    await callback_query.message.edit_reply_markup(None)
    await state.update_data({'for_what': ind})
    await CalculateState.next()

    await callback_query.message.answer(
        Text.CHOOSE_GENDER, reply_markup=get_gender_inline_keyboard()
    )


async def calculate_state_gender(
    callback_query: types.CallbackQuery, state: FSMContext
):
    answer = int(callback_query.data[len('gender_'):])  # fmt: skip
    await callback_query.message.delete()
    await state.update_data({'gender': answer})
    await CalculateState.next()

    await callback_query.message.answer(Text.INPUT_AGE)


async def calculate_state_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(Text.NUMBER)
        return
    answer = int(message.text)
    await state.update_data({'age': answer})
    await CalculateState.next()

    await message.answer(Text.INPUT_GROWTH)


async def calculate_state_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(Text.NUMBER)
        return
    await state.update_data({'growth': int(message.text)})
    await CalculateState.next()

    await message.answer(Text.INPUT_WEIGHT)


async def calculate_state_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(Text.NUMBER)
        return
    await state.update_data({'weight': int(message.text)})
    await CalculateState.next()

    await message.answer(
        Text.ACTIVITY,
        reply_markup=get_keyboard_of_nums(7, prefix='activity'),
    )


async def calculate_state_activity(
    callback_query: types.CallbackQuery, state: FSMContext
):
    await callback_query.message.delete()
    activity = int(callback_query.data[len('activity_'):])  # fmt: skip
    data = await state.get_data()
    result = kcal_limit(
        data['weight'], data['growth'], data['age'], data['gender'], activity
    )
    result_limits = limits(result, data['for_what'])
    await state.set_data({'result': result, 'limits': result_limits})
    user_unit = get_user_unit(callback_query.from_user.id)
    unit = MASS_UNITS[user_unit][0]

    if unit == 'oz':
        result_limits = [
            round(gram_to_ounce(value), 1) for value in result_limits
        ]
    await callback_query.message.answer(
        Text.LIMITS.format(result=result, result_limits=result_limits, u=unit),
        reply_markup=get_calculate_finish_inline_keyboard(),
    )
    await CalculateState.next()


async def calculate_state_waiting_for_finish(
    callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    ind = int(callback_query.data[len('calculate_finish_'):])  # fmt: skip
    await callback_query.message.delete()
    answer = bool(ind)
    if answer:
        data = await state.get_data()
        db_users.update_elem(
            {'user_id': callback_query.from_user.id},
            {
                'limits': {
                    'calories': data['result'],
                    'protein': data['limits'][0],
                    'fat': data['limits'][1],
                    'carb': data['limits'][2],
                }
            },
        )
    callback_query.message.from_user = callback_query.from_user
    await command_settings(callback_query.message)
    await state.finish()


# Record state
async def command_record(message: types.Message, state: FSMContext):
    await RecordState.weight.set()
    unit = get_user_unit(message.from_user.id)
    await state.set_data({'unit': unit})
    await message.answer(Text.INPUT_RECORD_WEIGHT)


async def callback_record(
    callback_query: types.CallbackQuery, state: FSMContext
):
    await callback_query.message.delete()
    callback_query.message.from_user = callback_query.from_user
    await command_record(callback_query.message, state)


async def record_state_weight(message: types.Message, state: FSMContext):
    try:
        answer = message.text.replace(',', '.')
        value = float(answer)
    except ValueError:
        await message.answer(Text.NUMBER)
        return
    unit = (await state.get_data())['unit']
    if unit == 'oz':
        value = ounce_to_gram(value)
    await state.update_data({'mass': value / 100})
    await RecordState.next()
    per = PER_MASS_TEXTS[unit]
    await message.answer(Text.INPUT_RECORD_PROTEIN.format(per=per))


async def record_state_protein(message: types.Message, state: FSMContext):
    try:
        answer = message.text.replace(',', '.')
        value = float(answer)
    except ValueError:
        await message.answer(Text.NUMBER)
        return
    data = await state.get_data()
    mass = data['mass']
    unit = data['unit']
    await state.update_data({'protein': value * mass})
    await RecordState.next()
    per = PER_MASS_TEXTS[unit]
    await message.answer(Text.INPUT_RECORD_FAT.format(per=per))


async def record_state_fat(message: types.Message, state: FSMContext):
    try:
        answer = message.text.replace(',', '.')
        value = float(answer)
    except ValueError:
        await message.answer(Text.NUMBER)
        return
    data = await state.get_data()
    mass = data['mass']
    unit = data['unit']
    await state.update_data({'fat': value * mass})
    await RecordState.next()
    per = PER_MASS_TEXTS[unit]
    await message.answer(Text.INPUT_RECORD_CARB.format(per=per))


async def record_state_carb(message: types.Message, state: FSMContext):
    try:
        answer = message.text.replace(',', '.')
        value = float(answer)
    except ValueError:
        await message.answer(Text.NUMBER)
        return
    mass = (await state.get_data())['mass']
    await state.update_data({'carb': value * mass, 'time': datetime.utcnow()})

    data = await state.get_data()
    data.pop('mass')
    data.pop('unit')
    db_users.update_elem(
        {'user_id': message.from_user.id},
        {'records': create_record(**data)},
        'push',
    )
    await state.finish()

    await message.answer(Word.RECORDED.capitalize())
    await command_statistics(message)


def register_user_handlers(dp: Dispatcher) -> None:
    # COMMANDS
    dp.register_message_handler(command_start, filters.CommandStart())
    dp.register_message_handler(
        command_calculate_calories, filters.Command('calculate'), state='*'
    )
    dp.register_message_handler(command_menu, filters.Command('menu'))
    dp.register_message_handler(
        command_record, filters.Command('record'), state='*'
    )
    dp.register_message_handler(command_statistics, filters.Command('stat'))
    dp.register_message_handler(command_records, filters.Command('records'))
    dp.register_message_handler(
        command_cancel, filters.Command('cancel'), state='*'
    )
    dp.register_message_handler(command_settings, filters.Command('settings'))

    # CALLBACKS
    dp.register_callback_query_handler(
        callback_calculate_calories,
        filters.Text(equals='calculate'),
        state='*',
    )
    dp.register_callback_query_handler(
        callback_open_menu, filters.Text(equals='to_menu')
    )
    dp.register_callback_query_handler(
        callback_record, filters.Text('record'), state='*'
    )
    dp.register_callback_query_handler(
        callback_statistics, filters.Text(startswith='statistics')
    )
    dp.register_callback_query_handler(
        callback_records, filters.Text(startswith='records')
    )
    dp.register_callback_query_handler(
        callback_settings, filters.Text('settings')
    )
    dp.register_callback_query_handler(
        callback_setting, filters.Regexp(r'^settings_[a-z]+$')
    )
    dp.register_callback_query_handler(
        settings_timezone_page,
        filters.Text(startswith='settings_zone_page_'),
        state='*',
    )
    dp.register_callback_query_handler(
        callback_setting_edit, filters.Regexp(r'^settings_[a-z]+_[^_]+$')
    )

    # STATES
    # Settings state
    dp.register_callback_query_handler(
        settings_state_timezone,
        filters.Text(startswith='settings_zone_'),
        state=SettingsState.time_zone,
    )
    dp.register_callback_query_handler(
        settings_state_unit,
        filters.Text(startswith='settings_unit_'),
        state=SettingsState.mass_unit,
    )

    # Calculate state
    dp.register_callback_query_handler(
        calculate_state_for_what, state=CalculateState.for_what
    )
    dp.register_callback_query_handler(
        calculate_state_gender, state=CalculateState.gender
    )
    dp.register_message_handler(calculate_state_age, state=CalculateState.age)
    dp.register_message_handler(
        calculate_state_growth, state=CalculateState.growth
    )
    dp.register_message_handler(
        calculate_state_weight, state=CalculateState.weight
    )
    dp.register_callback_query_handler(
        calculate_state_activity, state=CalculateState.activity
    )
    dp.register_callback_query_handler(
        calculate_state_waiting_for_finish,
        state=CalculateState.waiting_for_finish,
    )
    # Record state
    dp.register_message_handler(record_state_weight, state=RecordState.weight)
    dp.register_message_handler(
        record_state_protein, state=RecordState.protein
    )
    dp.register_message_handler(record_state_fat, state=RecordState.fat)
    dp.register_message_handler(record_state_carb, state=RecordState.carb)

    # Limits edit state
    dp.register_callback_query_handler(
        callback_limit, filters.Regexp(r'limits_[a-z]+$'), state='*'
    )
    dp.register_message_handler(command_limit_edit, state=LimitState.edit)

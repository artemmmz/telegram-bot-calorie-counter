from datetime import datetime
from math import ceil

from aiogram import Dispatcher, filters, types, exceptions
from aiogram.dispatcher import FSMContext

from config import TELEGRAM_BOT_SUPERUSER_ID
from db import Database
from db.structures import create_user, create_record
from db.utils import get_user
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
from utils.consts import RECORDS_PAGE_NUM, MASS_UNITS
from utils.states import CalculateState, RecordState, SettingsState
from utils.texts import gettext, Text, Word
from utils.utils import kcal_limit, limits

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
    user = db_users.get_records({'user_id': user_id}, limit=1)
    user['settings']['unit'] = MASS_UNITS[user['settings']['unit']][1]

    text = Text.SETTINGS.format(s=user['settings'])

    await message.answer(text, reply_markup=get_settings_inline_keyboard())


async def command_settings_unit(message: types.Message):
    await message.answer(Text.UNIT, reply_markup=get_unit_inline_keyboard())


async def command_settings_timezone(message: types.Message):
    await message.answer(Text.TIMEZONE, reply_markup=get_timezone_keyboard())


async def command_settings_unit_edit(
    message: types.Message, value: str | None = None
):
    db_users.update_elem(
        {'user_id': message.from_user.id},
        {'settings.unit': value},
    )
    await command_settings(message)


async def command_settings_timezone_edit(
    message: types.Message, value: str | None = None
):
    db_users.update_elem(
        {'user_id': message.from_user.id},
        {'settings.timezone': value},
    )
    await command_settings(message)


async def command_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await command_menu(message)


# CALLBACKS
async def callback_open_menu(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
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
    await callback_query.message.delete()
    await command_settings(callback_query.message)


async def callback_settings_unit(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await command_settings_unit(callback_query.message)


async def callback_settings_timezone(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await command_settings_timezone(callback_query.message)


async def callback_settings_unit_edit(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    value = callback_query.data[len('settings_unit_'):]  # fmt: skip
    callback_query.message.from_user = callback_query.from_user
    await command_settings_unit_edit(callback_query.message, value)


async def callback_settings_timezone_edit(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    value = callback_query.data[len('settings_zone_'):]  # fmt: skip
    callback_query.message.from_user = callback_query.from_user
    await command_settings_timezone_edit(callback_query.message, value)


async def callback_cancel(
    callback_query: types.CallbackQuery, state: FSMContext
):
    await callback_query.message.delete()
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

    await command_settings_timezone(callback_query.message)


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

    await callback_query.message.answer(
        Text.LIMITS.format(result=result, result_limits=result_limits),
        reply_markup=get_calculate_finish_inline_keyboard(),
    )
    await CalculateState.next()


async def calculate_state_waiting_for_finish(
    callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    ind = int(callback_query.data[len('calculate_finish_'):])  # fmt: skip
    if ind == 2:
        # TODO: write a change limits after calculate
        await callback_query.answer('Soon', show_alert=True)
        return
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
        await callback_query.message.answer('Limit saved')
    await command_menu(callback_query.message)
    await state.finish()


# Record state
async def command_record(message: types.Message):
    await RecordState.weight.set()
    await message.answer(Text.INPUT_RECORD_WEIGHT)


async def callback_record(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await command_record(callback_query.message)


async def record_state_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(Text.NUMBER)
        return
    answer = int(message.text)
    await state.update_data({'mass': answer / 100})
    await RecordState.next()

    await message.answer(Text.INPUT_RECORD_PROTEIN)


async def record_state_protein(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(Text.NUMBER)
        return
    answer = int(message.text)
    mass = (await state.get_data())['mass']
    await state.update_data({'protein': answer * mass})
    await RecordState.next()

    await message.answer(Text.INPUT_RECORD_FAT)


async def record_state_fat(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(Text.NUMBER)
        return
    answer = int(message.text)
    mass = (await state.get_data())['mass']
    await state.update_data({'fat': answer * mass})
    await RecordState.next()

    await message.answer(Text.INPUT_RECORD_CARB)


async def record_state_carb(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(Text.NUMBER)
        return
    answer = int(message.text)
    mass = (await state.get_data())['mass']
    await state.update_data({'carb': answer * mass, 'time': datetime.utcnow()})

    data = await state.get_data()
    data.pop('mass')
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
    dp.register_message_handler(command_record, filters.Command('record'))
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
    dp.register_callback_query_handler(callback_record, filters.Text('record'))
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
        callback_settings_unit, filters.Text('settings_unit')
    )
    dp.register_callback_query_handler(
        callback_settings_timezone, filters.Text('settings_zone')
    )
    dp.register_callback_query_handler(
        callback_settings_unit_edit, filters.Text(startswith='settings_unit_')
    )
    dp.register_callback_query_handler(
        settings_timezone_page, filters.Text(startswith='settings_zone_page_')
    )
    dp.register_callback_query_handler(
        callback_settings_timezone_edit,
        filters.Text(startswith='settings_zone_'),
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

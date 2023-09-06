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
from utils.utils import kcal_limit, limits
from utils.texts import gettext
from utils.states import CalculateState, RecordState, SettingsState

db_users = Database('users')
_ = gettext


# COMMANDS
async def command_start(message: types.Message):
    await message.answer(
        _('Hello!\nSelect your mass unit'),
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
        _(
            '<b>MENU</b>\n\n'
            '\t- Record(/record)'
            ' - record your calories by proteins, fats and carbs\n'
            '\t- Statistics(/stat)'
            ' - your calorie, protein, fat and carb statistics\n'
            '\t- Records(/records)'
            ' - list of your records\n'
            '\t- Settings(/settings)'
            ' - settings mass unit, timezone, language and etc.\n'
        ),
        parse_mode='HTML',
        reply_markup=get_menu_inline_keyboard(),
    )


async def command_profile(message: types.Message):
    await message.answer(_('Your profile\n'))


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

    unit = _(user['settings']['mass'])

    text = _(
        'Your statistics:\n\n'
        'Protein: {s[protein]}/{l[protein]} {u}\n'
        'Fat: {s[fat]}/{l[fat]} {u}\n'
        'Carb: {s[carb]}/{l[carb]} {u}\n'
        'Calories: {s[calories]}/{l[calories]} kcal\n'
    ).format(
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
    unit = _(user['settings']['mass'])

    date_string = user['date_str']
    records_date = user['records_date']
    records_date_page = records_date[
        page * RECORDS_PAGE_NUM: (page + 1) * RECORDS_PAGE_NUM  # fmt: skip
    ]
    records = [
        _(
            '\tTime: {r[time_str]}\n'
            '\tProtein: {r[protein]} {unit}\n'
            '\tFat: {r[fat]} {unit}\n'
            '\tCarb: {r[carb]} {unit}\n'
            '\tCalories: {r[calories]} kcal\n'
        ).format(r=record, unit=unit)
        for record in records_date_page
    ]

    records_text = '\n'.join(records) if len(records) > 0 else 'Empty'
    text = _('List of records\n\n{rt}').format(rt=records_text)
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


async def command_settings(
    message: types.Message,
    setting: str | None = None,
    value: str | None = None,
):
    user_id = message.from_user.id
    user = db_users.get_records({'user_id': user_id}, limit=1)
    user['settings']['mass'] = MASS_UNITS[user['settings']['mass']]

    text = _(
        'SETTINGS\n\n'
        'Mass unit: {s[mass]}\n'
        'Timezone: UTC{s[utc]}\n\n'
        'What change?'
    ).format(s=user['settings'])

    await message.answer(text, reply_markup=get_settings_inline_keyboard())


async def command_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await command_menu(message)


# CALLBACKS
async def callback_calculate_calories(
    callback_query: types.CallbackQuery,
):
    await callback_query.message.delete()
    await command_calculate_calories(callback_query.message)


async def callback_open_menu(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await command_menu(callback_query.message)


async def callback_profile(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    callback_query.message.from_user = callback_query.from_user
    await command_profile(callback_query.message)


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
        params = None
        date_string, page = None, None
    else:
        params = params_raw.split('_')
        date_string = params[0]
        page = int(params[1][len('p'):])  # fmt: skip
    callback_query.message.from_user = callback_query.from_user
    try:
        await command_records(callback_query.message, date_string, page)
    except exceptions.MessageNotModified:
        await callback_query.answer(_('Error'), show_alert=True)


async def callback_settings(callback_query: types.CallbackQuery):
    params_raw = callback_query.data[len('settings_'):]  # fmt: skip
    callback_query.message.from_user = callback_query.from_user
    await callback_query.message.delete()
    setting, value = None, None
    if params_raw != '':
        params = params_raw.split('_')
        setting = params[0]
        if len(params) >= 2:
            value = params[1]
    await command_settings(callback_query.message, setting, value)


async def callback_cancel(
    callback_query: types.CallbackQuery, state: FSMContext
):
    await callback_query.message.delete()
    await command_cancel(callback_query.message, state)


# STATES
# Settings state
async def settings_state_unit(
    callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    await callback_query.message.delete()
    answer = callback_query.data[len('settings_unit_'):]  # fmt: skip
    await state.update_data({'mass': answer})
    await SettingsState.next()

    await callback_query.message.answer(
        _('Select your time zome'), reply_markup=get_timezone_keyboard()
    )


async def settings_state_time_zone_page(
    callback_query: types.CallbackQuery, state: FSMContext
):
    page = int(callback_query.data[len('zonepage_'):])  # fmt: skip
    await callback_query.message.edit_reply_markup(get_timezone_keyboard(page))


async def settings_state_time_zone(
    callback_query: types.CallbackQuery, state: FSMContext
):
    await callback_query.message.delete()
    answer = callback_query.data[len('settings_zone_'):]  # fmt: skip
    await state.update_data({'utc': answer})

    data = await state.get_data()
    db_users.update_elem(
        {'user_id': callback_query.from_user.id}, {'settings': data}
    )
    await state.finish()

    await callback_query.message.answer(
        _('Your choices saved\nCalculate your limits?'),
        reply_markup=get_settings_end_inline_keyboard(),
    )


# Calculate State
async def command_calculate_calories(message: types.Message):
    await CalculateState.for_what.set()
    await message.answer(
        _(
            'Choose what do you want:\n\n'
            '1. Weight gain\n'
            '2. Control of the diet\n'
            '3. For the weigth loss\n'
        ),
        reply_markup=get_keyboard_of_nums(3, prefix='for_what'),
    )


async def calculate_state_for_what(
    callback_query: types.CallbackQuery, state: FSMContext
):
    ind = int(callback_query.data[len('for_what_'):])  # fmt: skip
    await callback_query.message.edit_reply_markup(None)
    await state.update_data({'for_what': ind})
    await CalculateState.next()

    await callback_query.message.answer(
        _('Choose your gender'), reply_markup=get_gender_inline_keyboard()
    )


async def calculate_state_gender(
    callback_query: types.CallbackQuery, state: FSMContext
):
    answer = int(callback_query.data[len('gender_'):])  # fmt: skip
    await callback_query.message.delete()
    await state.update_data({'gender': answer})
    await CalculateState.next()

    await callback_query.message.answer(_('Input your age'))


async def calculate_state_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(_('It must be a number'))
        return
    await state.update_data({'age': int(message.text)})
    await CalculateState.next()

    await message.answer(_('Input your growth(rounded)'))


async def calculate_state_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(_('It must be a number'))
        return
    await state.update_data({'growth': int(message.text)})
    await CalculateState.next()

    await message.answer(_('Input your weight(rounded)'))


async def calculate_state_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(_('It must be a number'))
        return
    await state.update_data({'weight': int(message.text)})
    await CalculateState.next()

    await message.answer(
        _(
            'Choose your activity coefficient:\n\n'
            '1. Minimum physical activity\n'
            '2. Workout 3 times per week\n'
            '3. Workout 5 times per week\n'
            '4. Intensive workout 5 times per week\n'
            '5. Workout every day\n'
            '6. Intensive workout every day or 2 times per day\n'
            '7. Physical activity every day + physical work\n'
        ),
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
        _(
            'Your calorie limit: {result} kcal\n'
            'Your protein limit: {result_limits[0]} g\n'
            'Your fat limit: {result_limits[1]} g\n'
            'Your carb limit: {result_limits[2]} g\n'
            'Write this number to your calorie limit?'
        ).format(result=result, result_limits=result_limits),
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


async def calculate_state_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Cancel state')
    await command_menu(message)


# Record state
async def command_record(message: types.Message):
    await RecordState.weight.set()
    await message.answer(_('Input the weight of eaten'))


async def callback_record(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await command_record(callback_query.message)


async def record_state_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(_('It must be a number(gram)'))
        return
    answer = int(message.text)
    await state.update_data({'mass': answer / 100})
    await RecordState.next()

    await message.answer(_('Input the weight of protein per 100 grams'))


async def record_state_protein(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(_('It must be a number(gram)'))
        return
    answer = int(message.text)
    mass = (await state.get_data())['mass']
    await state.update_data({'protein': answer * mass})
    await RecordState.next()

    await message.answer(_('Input the weight of fat per 100 grams'))


async def record_state_fat(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(_('It must be a number(gram)'))
        return
    answer = int(message.text)
    mass = (await state.get_data())['mass']
    await state.update_data({'fat': answer * mass})
    await RecordState.next()

    await message.answer(_('Input the weight of fat per 100 grams'))


async def record_state_carb(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(_('It must be a number(gram)'))
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

    await message.answer(_('Recorded'))
    await command_statistics(message)


def register_user_handlers(dp: Dispatcher) -> None:
    # COMMANDS
    dp.register_message_handler(command_start, filters.CommandStart())
    dp.register_message_handler(
        command_calculate_calories, filters.Command('calculate')
    )
    dp.register_message_handler(command_menu, filters.Command('menu'))
    dp.register_message_handler(command_profile, filters.Command('profile'))
    dp.register_message_handler(command_record, filters.Command('record'))
    dp.register_message_handler(command_statistics, filters.Command('stat'))
    dp.register_message_handler(command_records, filters.Command('records'))
    dp.register_message_handler(
        command_cancel, filters.Command('cancel'), state='*'
    )
    dp.register_message_handler(command_settings, filters.Command('settings'))

    # CALLBACKS
    dp.register_callback_query_handler(
        callback_calculate_calories, filters.Text(equals='calculate_calorie')
    )
    dp.register_callback_query_handler(
        callback_open_menu, filters.Text(equals='to_menu')
    )
    dp.register_callback_query_handler(callback_record, filters.Text('record'))
    dp.register_callback_query_handler(
        callback_profile, filters.Text('profile')
    )
    dp.register_callback_query_handler(
        callback_statistics, filters.Text(startswith='statistics')
    )
    dp.register_callback_query_handler(
        callback_records, filters.Text(startswith='records')
    )
    dp.register_callback_query_handler(
        callback_settings, filters.Text(startswith='settings')
    )

    # STATES
    # Settings state
    dp.register_callback_query_handler(
        settings_state_time_zone_page,
        filters.Text(startswith='zonepage_'),
        state=SettingsState.time_zone,
    )
    dp.register_callback_query_handler(
        settings_state_time_zone,
        filters.Text(startswith='settings_zone_'),
        state=SettingsState.time_zone,
    )
    dp.register_callback_query_handler(
        settings_state_unit, state=SettingsState.mass_unit
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

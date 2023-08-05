from aiogram import Dispatcher, filters, types
from aiogram.dispatcher import FSMContext

from config import TELEGRAM_BOT_SUPERUSER_ID
from db.db import Database
from keyboards import (
    START_INLINE_KEYBOARD,
    GENDER_INLINE_KEYBOARD,
    MENU_INLINE_KEYBOARD,
    CALCULATE_FINISH_INLINE_KEYBOARD,
    get_keyboard_of_nums,
)
from utils.calculations import kcal_limit, limits
from utils.states import CalculateState

db_users = Database('users')


# COMMANDS
async def command_start(message: types.Message) -> None:
    await message.answer('Start', reply_markup=START_INLINE_KEYBOARD)
    user_id = message.from_user.id
    db_users.add_records(
        {
            'user_id': user_id,
            'is_superuser': user_id == TELEGRAM_BOT_SUPERUSER_ID,
            'is_admin': user_id == TELEGRAM_BOT_SUPERUSER_ID,
        }
    )


async def command_menu(message: types.Message) -> None:
    await message.answer('Menu', reply_markup=MENU_INLINE_KEYBOARD)


async def command_profile(message: types.Message) -> None:
    await message.answer(('Your profile\n'))


async def command_record(message: types.Message):
    ...


# CALLBACKS
async def callback_calculate_calories(
    callback_query: types.CallbackQuery,
) -> None:
    await callback_query.message.edit_reply_markup(None)
    await command_calculate_calories(callback_query.message)


async def callback_open_menu(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.edit_reply_markup(None)
    await command_menu(callback_query.message)


# STATES
# Calculate State
async def command_calculate_calories(message: types.Message) -> None:
    await CalculateState.for_what.set()
    await message.answer(
        (
            'Choose what do you want:\n\n'
            '1. Weight gain\n'
            '2. Control of the diet\n'
            '3. For the weigth loss\n'
        ),
        reply_markup=get_keyboard_of_nums(3, prefix='for_what'),
    )


async def calculate_state_for_what(
    callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    ind = int(callback_query.data[len('for_what_'):])  # fmt: skip
    await callback_query.message.edit_reply_markup(None)
    await state.update_data({'for_what': ind})
    await CalculateState.next()

    await callback_query.message.answer(
        'Choose your gender', reply_markup=GENDER_INLINE_KEYBOARD
    )


async def calculate_state_gender(
    callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    answer = int(callback_query.data[len('gender_'):])  # fmt: skip
    await callback_query.message.edit_reply_markup(None)
    await state.update_data({'gender': answer})
    await CalculateState.next()

    await callback_query.message.answer('Input your age')


async def calculate_state_age(
    message: types.Message, state: FSMContext
) -> None:
    if not message.text.isdigit():
        await message.answer("It must be a number")
        return
    await state.update_data({'age': int(message.text)})
    await CalculateState.next()

    await message.answer('Input your growth(rounded)')


async def calculate_state_growth(
    message: types.Message, state: FSMContext
) -> None:
    if not message.text.isdigit():
        await message.answer("It must be a number")
        return
    await state.update_data({'growth': int(message.text)})
    await CalculateState.next()

    await message.answer('Input your weight(rounded)')


async def calculate_state_weight(
    message: types.Message, state: FSMContext
) -> None:
    if not message.text.isdigit():
        await message.answer("It must be a number")
        return
    await state.update_data({'weight': int(message.text)})
    await CalculateState.next()

    await message.answer(
        (
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
) -> None:
    await callback_query.message.edit_reply_markup(None)
    activity = int(callback_query.data[len('activity_'):])  # fmt: skip
    data = await state.get_data()
    result = kcal_limit(
        data['weight'], data['growth'], data['age'], data['gender'], activity
    )
    result_limits = limits(result, data['for_what'])
    await state.set_data({'result': result, 'limits': result_limits})

    await callback_query.message.answer(
        (
            f'Your calorie limit: {result} kcal\n'
            f'Your protein limit: {result_limits[0]} g\n'
            f'Your fat limit: {result_limits[1]} g\n'
            f'Your carb limit: {result_limits[2]} g\n'
            'Write this number to your calorie limit?'
        ),
        reply_markup=CALCULATE_FINISH_INLINE_KEYBOARD,
    )
    await CalculateState.next()


async def calculate_state_waiting_for_finish(
    callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    ind = int(callback_query.data[len('calculate_finish_'):])  # fmt: skip
    if ind == 2:
        # TODO: write a change limits after calculate
        return
    await callback_query.message.edit_reply_markup(None)
    answer = bool(ind)
    if answer:
        data = await state.get_data()
        db_users.update_elem(
            {'user_id': callback_query.from_user.id},
            {
                'calorie_limit': data['result'],
                'protein_limit': data['limits'][0],
                'fat_limit': data['limits'][1],
                'carb_limit': data['limits'][2],
            },
        )
        await callback_query.message.answer('Limit saved')
    await callback_query.message.answer('Finish')
    await command_menu(callback_query.message)
    await state.finish()


async def calculate_state_cancel(
    message: types.Message, state: FSMContext
) -> None:
    await state.finish()
    await message.answer('Cancel state')
    await command_menu(message)


def register_user_handlers(dp: Dispatcher) -> None:
    # COMMANDS
    dp.register_message_handler(command_start, filters.CommandStart())
    dp.register_message_handler(
        command_calculate_calories, filters.Command('calculate')
    )
    dp.register_message_handler(command_menu, filters.Command('menu'))
    dp.register_message_handler(command_profile, filters.Command('profile'))
    dp.register_message_handler(command_record, filters.Command('record'))

    # CALLBACKS
    dp.register_callback_query_handler(
        callback_calculate_calories, filters.Text(equals='calculate_calorie')
    )
    dp.register_callback_query_handler(
        callback_open_menu, filters.Text(equals='to_menu')
    )

    # STATES
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

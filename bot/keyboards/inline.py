from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_yesno_keyboard(row_width=2, prefix=None) -> InlineKeyboardMarkup:
    if prefix:
        prefix = f'{prefix}_'
    keyboard = InlineKeyboardMarkup(row_width)
    keyboard.add(
        InlineKeyboardButton('Yes', callback_data=f'{prefix}1'),
        InlineKeyboardButton('No', callback_data=f'{prefix}0'),
    )
    return keyboard


def get_keyboard_of_nums(
    to, row_width=1, prefix: str | None = None
) -> InlineKeyboardMarkup:
    if prefix:
        prefix = f'{prefix}_'
    keyboard = InlineKeyboardMarkup(row_width)
    keyboard.add(
        *[
            InlineKeyboardButton(f'{i + 1}', callback_data=f'{prefix}{i}')
            for i in range(to)
        ]
    )
    return keyboard


START_INLINE_KEYBOARD = InlineKeyboardMarkup()
START_INLINE_KEYBOARD.row(
    InlineKeyboardButton(
        'Calculate calorie', callback_data='calculate_calorie'
    )
)

MENU_INLINE_KEYBOARD = InlineKeyboardMarkup()
MENU_INLINE_KEYBOARD.row(
    InlineKeyboardButton('Record', callback_data='record')
)
MENU_INLINE_KEYBOARD.row(
    InlineKeyboardButton('Profile', callback_data='profile')
)

PROFILE_INLINE_KEYBOARD = InlineKeyboardMarkup()
PROFILE_INLINE_KEYBOARD.row(
    InlineKeyboardButton('Change calorie', callback_data='change_calorie')
)
PROFILE_INLINE_KEYBOARD.row(
    InlineKeyboardButton(
        'Calculate calorie', callback_data='calculate_calorie'
    )
)
PROFILE_INLINE_KEYBOARD.row(InlineKeyboardButton('Change language(soon)'))

LANGUAGE_INLINE_KEYBOARD = InlineKeyboardMarkup()
LANGUAGE_INLINE_KEYBOARD.add(
    InlineKeyboardButton('English', callback_data='language_en')
)

UNIT_INLINE_KEYBOARD = InlineKeyboardMarkup()
UNIT_INLINE_KEYBOARD.add(
    InlineKeyboardButton('Gram', callback_data='unit_g'),
    InlineKeyboardButton('Ounce', callback_data='unit_oz'),
)

TIME_ZONE_INLINE_KEYBOARD = InlineKeyboardMarkup()
TIME_ZONE_INLINE_KEYBOARD.add(
    InlineKeyboardButton('UTC-3', callback_data='zone_-3'),
    InlineKeyboardButton('UTC-2', callback_data='zone_-2'),
    InlineKeyboardButton('UTC-1', callback_data='zone_-1'),
    InlineKeyboardButton('UTC+0', callback_data='zone_+0'),
    InlineKeyboardButton('UTC+1', callback_data='zone_+1'),
    InlineKeyboardButton('UTC+2', callback_data='zone_+2'),
    InlineKeyboardButton('UTC+3', callback_data='zone_+3'),
)

SETTINGS_END_INLINE_KEYBOARD = InlineKeyboardMarkup()
SETTINGS_END_INLINE_KEYBOARD.add(
    InlineKeyboardButton('Yes', callback_data='calculate_calorie'),
    InlineKeyboardButton('No', callback_data='to_menu'),
)

GENDER_INLINE_KEYBOARD = InlineKeyboardMarkup()
GENDER_INLINE_KEYBOARD.row(
    InlineKeyboardButton('Male', callback_data='gender_0'),
    InlineKeyboardButton('Female', callback_data='gender_1'),
)

CALCULATE_FINISH_INLINE_KEYBOARD = get_yesno_keyboard(
    prefix='calculate_finish'
)
CALCULATE_FINISH_INLINE_KEYBOARD.add(
    InlineKeyboardButton('Change value', callback_data='calculate_finish_2')
)

OPEN_MENU_INLINE_KEYBOARD = InlineKeyboardMarkup()
OPEN_MENU_INLINE_KEYBOARD.add(
    InlineKeyboardButton('Go to menu', callback_data='to_menu')
)

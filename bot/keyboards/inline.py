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
MENU_INLINE_KEYBOARD.row(InlineKeyboardButton('Write', callback_data='write'))
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

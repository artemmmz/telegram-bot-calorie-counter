from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .utils import (
    TIME_ZONES,
    TIME_ZONE_START_PAGE,
    get_prev_day,
    get_next_day,
)


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


def get_timezone_keyboard(page=-1, rows=3, cols=3):
    if page == -1:
        page = TIME_ZONE_START_PAGE
    keyboard = InlineKeyboardMarkup(row_width=rows)
    keyboard.add(
        *[
            InlineKeyboardButton(
                f'UTC{tz}', callback_data=f'zone_{tz.zfill(3)}'
            )
            for tz in TIME_ZONES[
                rows * cols * page: rows * cols * (page + 1)  # fmt: skip
            ]
        ]
    )

    control_row = []
    if page > 0:
        control_row.append(
            InlineKeyboardButton('<<', callback_data=f'zonepage_{page - 1}')
        )
    if page < len(TIME_ZONES) / (rows * cols) - 1:
        control_row.append(
            InlineKeyboardButton('>>', callback_data=f'zonepage_{page + 1}')
        )
    keyboard.row(*control_row)
    return keyboard


def get_statistics_keyboard(date: str):
    keyboard = InlineKeyboardMarkup(1)
    keyboard.row(
        InlineKeyboardButton(
            '<<', callback_data=f'statistics_{get_prev_day(date)}'
        ),
        InlineKeyboardButton(
            '>>', callback_data=f'statistics_{get_next_day(date)}'
        ),
    )
    keyboard.add(
        InlineKeyboardButton('Menu', callback_data='to_menu'),
    )
    return keyboard


def get_records_keyboard(date: str, page: int, pages: int):
    keyboard = InlineKeyboardMarkup(1)
    if pages > 0:
        keyboard.row(
            InlineKeyboardButton(
                '<<', callback_data=f'records_{date}_p{max(0, page - 1)}'
            ),
            InlineKeyboardButton(
                f'Page {page + 1}/{pages}', callback_data=f'records_{date}_p0'
            ),
            InlineKeyboardButton(
                '>>',
                callback_data=f'records_{date}_p{min(pages - 1, page + 1)}',
            ),
        )
    keyboard.row(
        InlineKeyboardButton(
            '<<', callback_data=f'records_{get_prev_day(date)}_p0'
        ),
        InlineKeyboardButton(f'{date}', callback_data=''),
        InlineKeyboardButton(
            '>>', callback_data=f'records_{get_next_day(date)}_p0'
        ),
    )
    keyboard.add(
        InlineKeyboardButton('Menu', callback_data='to_menu'),
    )
    return keyboard


START_INLINE_KEYBOARD = InlineKeyboardMarkup()
START_INLINE_KEYBOARD.row(
    InlineKeyboardButton(
        'Calculate calorie', callback_data='calculate_calorie'
    )
)

MENU_INLINE_KEYBOARD = InlineKeyboardMarkup(1)
MENU_INLINE_KEYBOARD.add(
    InlineKeyboardButton('Record', callback_data='record'),
    InlineKeyboardButton('Statistics', callback_data='statistics'),
    InlineKeyboardButton('Records', callback_data='records'),
    InlineKeyboardButton('Settings', callback_data='settings'),
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

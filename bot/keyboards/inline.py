from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.consts import TIME_ZONES, MASS_UNITS, TIME_ZONE_START_PAGE
from utils.texts import Text
from .utils import (
    get_prev_day,
    get_next_day,
)


def get_yesno_keyboard(row_width=2, prefix=None) -> InlineKeyboardMarkup:
    if prefix:
        prefix = f'{prefix}_'
    keyboard = InlineKeyboardMarkup(row_width)
    keyboard.add(
        InlineKeyboardButton(Text.YES_CAP, callback_data=f'{prefix}1'),
        InlineKeyboardButton(Text.NO_CAP, callback_data=f'{prefix}0'),
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
                f'UTC{tz}', callback_data=f'settings_zone_{tz}'
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


def get_statistics_keyboard(date: str, today_date: str):
    keyboard = InlineKeyboardMarkup(1)
    keyboard.row(
        InlineKeyboardButton(
            '<<', callback_data=f'statistics_{get_prev_day(date)}'
        ),
        InlineKeyboardButton(date, callback_data=f'statistics_{today_date}'),
        InlineKeyboardButton(
            '>>', callback_data=f'statistics_{get_next_day(date)}'
        ),
    )
    keyboard.add(
        InlineKeyboardButton(
            f'<<< {Text.MENU.upper()}', callback_data='to_menu'
        ),
    )
    return keyboard


def get_records_keyboard(date: str, today_date: str, page: int, pages: int):
    keyboard = InlineKeyboardMarkup(1)
    if pages > 1:
        keyboard.row(
            InlineKeyboardButton(
                '<<', callback_data=f'records_{date}_p{max(0, page - 1)}'
            ),
            InlineKeyboardButton(
                f'{Text.PAGE_CAP} {page + 1}/{pages}',
                callback_data=f'records_{date}_p0',
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
        InlineKeyboardButton(
            f'{date}', callback_data=f'records_{today_date}_p0'
        ),
        InlineKeyboardButton(
            '>>', callback_data=f'records_{get_next_day(date)}_p0'
        ),
    )
    keyboard.add(
        InlineKeyboardButton(f'<<< {Text.MENU_UP}', callback_data='to_menu'),
    )
    return keyboard


def get_start_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            Text.CALCULATE_CAP, callback_data='calculate_calorie'
        )
    )
    return keyboard


def get_menu_inline_keyboard():
    keyboard = InlineKeyboardMarkup(1)
    keyboard.add(
        InlineKeyboardButton(Text.RECORD_CAP, callback_data='record'),
        InlineKeyboardButton(Text.STATISTICS_CAP, callback_data='statistics'),
        InlineKeyboardButton(Text.RECORDS_CAP, callback_data='records'),
        InlineKeyboardButton(Text.SETTINGS_CAP, callback_data='settings'),
    )
    return keyboard


def get_unit_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        *[
            InlineKeyboardButton(
                text.capitalize(), callback_data=f'settings_unit_{unit}'
            )
            for unit, text in MASS_UNITS.items()
        ]
    )
    return keyboard


def get_settings_end_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(Text.YES_CAP, callback_data='calculate_calorie'),
        InlineKeyboardButton(Text.NO_CAP, callback_data='to_menu'),
    )
    return keyboard


def get_gender_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(Text.MALE_CAP, callback_data='gender_0'),
        InlineKeyboardButton(Text.FEMALE_CAP, callback_data='gender_1'),
    )
    return keyboard


def get_calculate_finish_inline_keyboard():
    keyboard = get_yesno_keyboard(prefix='calculate_finish')
    keyboard.add(
        InlineKeyboardButton(
            Text.CHANGE_VALUE_CAP, callback_data='calculate_finish_2'
        )
    )
    return keyboard


def get_settings_inline_keyboard():
    keyboard = InlineKeyboardMarkup(3)
    keyboard.row(
        InlineKeyboardButton(
            Text.MASS_UNIT_CAP, callback_data='settings_unit'
        ),
        InlineKeyboardButton(Text.TIMEZONE_CAP, callback_data='settings_zone'),
    )
    keyboard.row(
        InlineKeyboardButton(f'<<< {Text.MENU_UP}', callback_data='to_menu')
    )
    return keyboard

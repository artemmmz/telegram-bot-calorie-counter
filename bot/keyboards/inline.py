from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.consts import TIME_ZONES, MASS_UNITS, TIME_ZONE_START_PAGE
from utils.texts import Word
from .utils import (
    get_prev_day,
    get_next_day,
)


def get_yesno_keyboard(row_width=2, prefix=None) -> InlineKeyboardMarkup:
    if prefix:
        prefix = f'{prefix}_'
    keyboard = InlineKeyboardMarkup(row_width)
    keyboard.add(
        InlineKeyboardButton(
            Word.YES.capitalize(), callback_data=f'{prefix}1'
        ),
        InlineKeyboardButton(Word.NO.capitalize(), callback_data=f'{prefix}0'),
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
                f'UTC{tz}', callback_data=f'settings_timezone_{tz}'
            )
            for tz in TIME_ZONES[
                rows * cols * page: rows * cols * (page + 1)  # fmt: skip
            ]
        ]
    )

    control_row = []
    if page > 0:
        control_row.append(
            InlineKeyboardButton(
                '<<', callback_data=f'settings_zone_page_{page - 1}'
            )
        )
    if page < len(TIME_ZONES) / (rows * cols) - 1:
        control_row.append(
            InlineKeyboardButton(
                '>>', callback_data=f'settings_zone_page_{page + 1}'
            )
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
            f'<<< {Word.MENU.upper()}', callback_data='to_menu'
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
                f'{Word.PAGE.capitalize()} {page + 1}/{pages}',
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
        InlineKeyboardButton(
            f'<<< {Word.MENU.upper()}', callback_data='to_menu'
        ),
    )
    return keyboard


def get_start_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            Word.CALCULATE.capitalize(), callback_data='calculate_calorie'
        )
    )
    return keyboard


def get_menu_inline_keyboard():
    keyboard = InlineKeyboardMarkup(1)
    keyboard.add(
        InlineKeyboardButton(Word.RECORD.capitalize(), callback_data='record'),
        InlineKeyboardButton(
            Word.STATISTICS.capitalize(), callback_data='statistics'
        ),
        InlineKeyboardButton(
            Word.RECORDS.capitalize(), callback_data='records'
        ),
        InlineKeyboardButton(
            Word.CALCULATE.capitalize(), callback_data='calculate'
        ),
        InlineKeyboardButton(
            Word.SETTINGS.capitalize(), callback_data='settings'
        ),
    )
    return keyboard


def get_unit_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        *[
            InlineKeyboardButton(
                word[1].capitalize(), callback_data=f'settings_unit_{unit}'
            )
            for unit, word in MASS_UNITS.items()
        ]
    )
    return keyboard


def get_settings_end_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(Word.YES.capitalize(), callback_data='calculate'),
        InlineKeyboardButton(Word.NO.capitalize(), callback_data='to_menu'),
    )
    return keyboard


def get_gender_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(Word.MALE.capitalize(), callback_data='gender_0'),
        InlineKeyboardButton(
            Word.FEMALE.capitalize(), callback_data='gender_1'
        ),
    )
    return keyboard


def get_calculate_finish_inline_keyboard():
    return get_yesno_keyboard(prefix='calculate_finish')


def get_settings_inline_keyboard():
    keyboard = InlineKeyboardMarkup(3)
    keyboard.row(
        InlineKeyboardButton(
            Word.MASS_UNIT.capitalize(), callback_data='settings_unit'
        ),
        InlineKeyboardButton(
            Word.TIMEZONE.capitalize(), callback_data='settings_timezone'
        ),
    )
    keyboard.row(
        InlineKeyboardButton(
            Word.PROTEIN.capitalize(), callback_data='limits_protein'
        ),
        InlineKeyboardButton(
            Word.FAT.capitalize(), callback_data='limits_fat'
        ),
        InlineKeyboardButton(
            Word.CARB.capitalize(), callback_data='limits_carb'
        ),
    )
    keyboard.row(
        InlineKeyboardButton(
            f'<<< {Word.MENU.upper()}', callback_data='to_menu'
        )
    )
    return keyboard

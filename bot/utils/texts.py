from typing import Any
from aiogram.contrib.middlewares.i18n import I18nMiddleware

from config import LOCALES_DIR

i18n = I18nMiddleware('bot', LOCALES_DIR)

_ = gettext = i18n.lazy_gettext


class __Text(object):
    YES = _('yes')
    NO = _('no')

    MENU = _('menu')
    CALCULATE = _('calculate')
    RECORD = _('record')
    STATISTICS = _('statistics')
    RECORDS = _('records')
    SETTINGS = _('settings')

    PAGE = _('page')

    MALE = _('male')
    FEMALE = _('female')

    CHANGE_VALUE = _('change value')

    MASS_UNIT = _('mass unit')
    TIMEZONE = _('timezone')

    GRAM_SHORT = _('g')
    GRAM = _('gram')

    OUNCE_SHORT = _('oz')
    OUNCE = _('ounce')

    def __getattribute__(self, __name: str) -> Any:
        method = __name.split('_')[-1]
        if method not in ['CAP', 'UP']:
            method = ''
        name = __name
        if len(method) > 0:
            name = __name[: -len(f'_{method}')]
        value = super().__getattribute__(name)
        if method == 'CAP':
            return value.capitalize()
        if method == 'UP':
            return value.upper()
        return value


Text = __Text()

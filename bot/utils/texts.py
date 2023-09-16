from aiogram.contrib.middlewares.i18n import I18nMiddleware

from config import LOCALES_DIR

i18n = I18nMiddleware('bot', LOCALES_DIR)

_ = gettext = i18n.lazy_gettext


class Word:
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

    EMPTY = _('empty')
    ERROR = _('error')
    RECORDED = _('recorded')

    PROTEIN = _('protein')
    FAT = _('fat')
    CARB = _('carb')


class Text:
    HELLO = _('Hello!\n{t}')
    MENU = _(
        '<b>MENU</b>\n\n'
        '\t- Record(/record)'
        ' - record your calories by proteins, fats and carbs\n'
        '\t- Statistics(/stat)'
        ' - your calorie, protein, fat and carb statistics\n'
        '\t- Records(/records)'
        ' - list of your records\n'
        '\t- Calculate(/calculate)'
        ' - calculate your calorie, protein, fat and carb limits\n'
        '\t- Settings(/settings)'
        ' - settings mass unit, timezone, language and etc.\n'
    )
    STATISTICS = _(
        '<b>STATISTICS</b>:\n\n'
        'Protein: {s[protein]}/{l[protein]} {u}\n'
        'Fat: {s[fat]}/{l[fat]} {u}\n'
        'Carb: {s[carb]}/{l[carb]} {u}\n'
        'Calories: {s[calories]}/{l[calories]} kcal\n'
    )
    RECORD = _(
        '\tTime: {r[time_str]}\n'
        '\tProtein: {r[protein]} {unit}\n'
        '\tFat: {r[fat]} {unit}\n'
        '\tCarb: {r[carb]} {unit}\n'
        '\tCalories: {r[calories]} kcal\n'
    )
    RECORDS = _('List of records\n\n{rt}')
    SETTINGS = _(
        '<b>SETTINGS</b>\n\n'
        'Mass unit: <code>{s[unit]}</code>\n'
        'Timezone: <code>UTC{s[timezone]}</code>\n\n'
        'Protein limit: <code>{l[protein]} {u}</code>\n'
        'Fat limit: <code>{l[fat]} {u}</code>\n'
        'Carb limit: <code>{l[carb]} {u}</code>\n\n'
        'What change?'
    )
    UNIT = _("Select your mass unit")
    TIMEZONE = _('Select your time zone')
    SETTINGS_END = _('Your choices saved\nCalculate your limits?')
    FOR_WHAT = _(
        'Choose what do you want:\n\n'
        '1. Weight gain\n'
        '2. Control of the diet\n'
        '3. For the weight loss\n'
    )
    CHOOSE_GENDER = _('Choose your gender')
    NUMBER = _('It must be a number')
    INPUT_AGE = _('Input your age')
    INPUT_GROWTH = _('Input your growth(rounded)')
    INPUT_WEIGHT = _('Input your weight(rounded)')
    ACTIVITY = _(
        'Choose your activity coefficient:\n\n'
        '1. Minimum physical activity\n'
        '2. Workout 3 times per week\n'
        '3. Workout 5 times per week\n'
        '4. Intensive workout 5 times per week\n'
        '5. Workout every day\n'
        '6. Intensive workout every day or 2 times per day\n'
        '7. Physical activity every day + physical work\n'
    )
    LIMITS = _(
        'Your calorie limit: {result} kcal\n'
        'Your protein limit: {result_limits[0]} {u}\n'
        'Your fat limit: {result_limits[1]} {u}\n'
        'Your carb limit: {result_limits[2]} {u}\n'
        'Write this number to your calorie limit?'
    )
    INPUT_RECORD_WEIGHT = _('Input the weight of eaten')
    INPUT_RECORD_PROTEIN = _('Input the weight of protein {per}')
    INPUT_RECORD_FAT = _('Input the weight of fat {per}')
    INPUT_RECORD_CARB = _('Input the weight of carb per {per}')
    RECORD_PER_GRAMS = _('per 100 grams')
    RECORD_PER_OUNCES = _('per 3.5 ounces')
    INPUT_LIMIT_PROTEIN = _('Input a limit of protein per day')
    INPUT_LIMIT_FAT = _('Input a limit of fat per day')
    INPUT_LIMIT_CARB = _('Input a limit of carb per day')

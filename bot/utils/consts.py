from utils.texts import Word, Text


RECORDS_PAGE_NUM = 3
TIME_ZONE_START_PAGE = 1

MASS_UNITS = {
    'g': (Word.GRAM_SHORT, Word.GRAM),
    'oz': (Word.OUNCE_SHORT, Word.OUNCE),
}
PER_MASS_TEXTS = {'g': Text.RECORD_PER_GRAMS, 'oz': Text.RECORD_PER_OUNCES}
TIME_ZONES = [
    '-12',
    '-11',
    '-10',
    '-09',
    '-08',
    '-07',
    '-06',
    '-05',
    '-04',
    '-03',
    '-02',
    '-01',
    '+00',
    '+01',
    '+02',
    '+03',
    '+04',
    '+05',
    '+06',
    '+07',
    '+08',
    '+09',
    '+10',
    '+11',
    '+12',
    '+13',
    '+14',
]

USER_RECORDS_DEFAULT_VALUES = {
    'time': None,
    'protein': 0,
    'fat': 0,
    'carb': 0,
}

USER_DEFAULT_VALUES = {
    'user_id': None,
    'is_admin': False,
    'is_superuser': False,
    'limits': {'calories': 0, 'protein': 0, 'fat': 0, 'carb': 0},
    'settings': {'language': 'en-uk', 'utc': '+00', 'mass': 'g'},
    'records': [],
}


def create_user(**kwargs) -> dict:
    user = USER_DEFAULT_VALUES
    for index, value in kwargs.items():
        user[index] = value
    return user


def create_record(**kwargs) -> dict:
    record = USER_RECORDS_DEFAULT_VALUES
    for index, value in kwargs.items():
        record[index] = value
    return record

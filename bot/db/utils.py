from db import Database

db_users = Database('users')


def get_aggregate_records(user_id: int | str, date_string: str):
    return db_users.collection.aggregate(
        [
            {'$match': {'user_id': user_id}},
            {
                '$project': {
                    'start_date': {
                        '$dateFromString': {
                            'dateString': date_string,
                            'timezone': '$settings.utc',
                        }
                    },
                    'settings.mass': 1,
                    'limits': 1,
                    'records': 1,
                }
            },
            {
                '$set': {
                    'end_date': {
                        '$dateAdd': {
                            'startDate': '$start_date',
                            'unit': 'day',
                            'amount': 1,
                        }
                    }
                }
            },
            {'$unwind': '$records'},
            {
                '$match': {
                    '$expr': {
                        '$or': [
                            {
                                '$and': [
                                    {'$gte': ['$records.time', '$start_date']},
                                    {'$gte': ['$end_date', '$records.time']},
                                ]
                            },
                            {'$eq': ['$records.time', None]},
                        ]
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'limits': {'$first': '$limits'},
                    'protein': {'$sum': '$records.protein'},
                    'fat': {'$sum': '$records.fat'},
                    'carb': {'$sum': '$records.carb'},
                    'unit': {'$first': '$settings.mass'},
                }
            },
            {
                '$project': {
                    'unit': 1,
                    'limits': 1,
                    'records': {
                        'calories': {
                            '$toInt': {
                                '$sum': [
                                    {'$multiply': ['$protein', 4]},
                                    {'$multiply': ['$fat', 9]},
                                    {'$multiply': ['$carb', 4]},
                                ]
                            }
                        },
                        'protein': {
                            '$cond': {
                                'if': {'$eq': ['$settings.mass', 'oz']},
                                'then': {
                                    '$round': [
                                        {'$divide': ['$protein', 28.3495]},
                                        1,
                                    ]
                                },
                                'else': {'$toInt': ['$protein']},
                            }
                        },
                        'fat': {
                            '$cond': {
                                'if': {'$eq': ['$settings.mass', 'oz']},
                                'then': {
                                    '$round': [
                                        {'$divide': ['$fat', 28.3495]},
                                        1,
                                    ]
                                },
                                'else': {'$toInt': ['$fat']},
                            }
                        },
                        'carb': {
                            '$cond': {
                                'if': {'$eq': ['$settings.mass', 'oz']},
                                'then': {
                                    '$round': [
                                        {'$divide': ['$carb', 28.3495]},
                                        1,
                                    ]
                                },
                                'else': {'$toInt': ['$carb']},
                            }
                        },
                    },
                }
            },
        ]
    )

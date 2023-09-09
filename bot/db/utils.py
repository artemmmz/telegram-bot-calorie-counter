from db import Database

from datetime import datetime

db_users = Database('users')


def get_user(user_id: int, __date_string: str | None = None):
    query = [
        {'$match': {'user_id': user_id}},
        {
            '$facet': {
                'other': [],
                'records_conv': [
                    {'$unwind': '$records'},
                    {
                        '$project': {
                            'time': '$records.time',
                            'time_str': {
                                '$dateToString': {
                                    'date': '$records.time',
                                    'format': '%H:%M',
                                    'timezone': '$settings.timezone',
                                }
                            },
                            'calories': {
                                '$toInt': {
                                    '$sum': [
                                        {'$multiply': ['$records.protein', 4]},
                                        {'$multiply': ['$records.fat', 9]},
                                        {'$multiply': ['$records.carb', 4]},
                                    ]
                                }
                            },
                            'protein': {
                                '$cond': {
                                    'if': {'$eq': ['$settings.unit', 'oz']},
                                    'then': {
                                        '$round': [
                                            {
                                                '$divide': [
                                                    '$records.protein',
                                                    28.3495,
                                                ]
                                            },
                                            1,
                                        ]
                                    },
                                    'else': {'$toInt': ['$records.protein']},
                                }
                            },
                            'fat': {
                                '$cond': {
                                    'if': {'$eq': ['$settings.unit', 'oz']},
                                    'then': {
                                        '$round': [
                                            {
                                                '$divide': [
                                                    '$records.fat',
                                                    28.3495,
                                                ]
                                            },
                                            1,
                                        ]
                                    },
                                    'else': {'$toInt': ['$records.fat']},
                                }
                            },
                            'carb': {
                                '$cond': {
                                    'if': {'$eq': ['$settings.unit', 'oz']},
                                    'then': {
                                        '$round': [
                                            {
                                                '$divide': [
                                                    '$records.carb',
                                                    28.3495,
                                                ]
                                            },
                                            1,
                                        ]
                                    },
                                    'else': {'$toInt': ['$records.carb']},
                                }
                            },
                        }
                    },
                ],
            }
        },
        {
            '$replaceRoot': {
                'newRoot': {'$mergeObjects': ['$$ROOT', {'$first': '$other'}]}
            }
        },
        {'$unset': 'other'},
    ]
    if __date_string:
        record_query = [
            {
                '$set': {
                    'date_str': __date_string,
                    'today_date': {
                        '$dateToParts': {
                            'date': datetime.utcnow(),
                            'timezone': '$settings.timezone',
                        }
                    },
                }
            },
            {
                '$set': {
                    'start_date': {
                        '$cond': {
                            'if': {'$eq': ['$date_str', 'today']},
                            'then': {
                                '$dateFromParts': {
                                    'year': '$today_date.year',
                                    'month': '$today_date.month',
                                    'day': '$today_date.day',
                                    'timezone': '$settings.timezone',
                                }
                            },
                            'else': {
                                '$dateFromString': {
                                    'dateString': '$date_str',
                                    'timezone': '$settings.timezone',
                                }
                            },
                        }
                    },
                    'today_str': {
                        '$dateToString': {
                            'date': {
                                '$dateFromParts': {
                                    'year': '$today_date.year',
                                    'month': '$today_date.month',
                                    'day': '$today_date.day',
                                }
                            },
                            'format': '%Y-%m-%d',
                        }
                    },
                }
            },
            {
                '$set': {
                    'date_str': {
                        '$cond': {
                            'if': {'$eq': ['$date_str', 'today']},
                            'then': '$today_str',
                            'else': '$date_str',
                        }
                    },
                    'end_date': {
                        '$dateAdd': {
                            'startDate': '$start_date',
                            'unit': 'day',
                            'amount': 1,
                        }
                    },
                }
            },
            {
                '$facet': {
                    'other': [],
                    'records_date': [
                        {'$unwind': '$records_conv'},
                        {
                            '$match': {
                                '$expr': {
                                    '$or': [
                                        {
                                            '$and': [
                                                {
                                                    '$gte': [
                                                        '$records_conv.time',
                                                        '$start_date',
                                                    ]
                                                },
                                                {
                                                    '$gte': [
                                                        '$end_date',
                                                        '$records_conv.time',
                                                    ]
                                                },
                                            ]
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            '$project': {
                                'time_str': '$records_conv.time_str',
                                'protein': '$records_conv.protein',
                                'fat': '$records_conv.fat',
                                'carb': '$records_conv.carb',
                                'calories': '$records_conv.calories',
                            }
                        },
                    ],
                }
            },
            {
                '$replaceRoot': {
                    'newRoot': {
                        '$mergeObjects': ['$$ROOT', {'$first': '$other'}]
                    }
                }
            },
            {
                '$set': {
                    'statistics': {
                        'protein': {'$sum': '$records_date.protein'},
                        'fat': {'$sum': '$records_date.fat'},
                        'carb': {'$sum': '$records_date.carb'},
                        'calories': {'$sum': '$records_date.calories'},
                    }
                }
            },
            {'$unset': ['other', 'start_date', 'end_date', 'today_date']},
        ]
        query = [*query, *record_query]
    answer = db_users.collection.aggregate(query)
    if answer.alive:
        return list(answer)[0]
    else:
        return None

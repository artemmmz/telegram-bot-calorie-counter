from db import Database

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
                                    'timezone': '$settings.utc',
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
                                    'if': {'$eq': ['$settings.mass', 'oz']},
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
                                    'if': {'$eq': ['$settings.mass', 'oz']},
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
                                    'if': {'$eq': ['$settings.mass', 'oz']},
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
        stat_query = [
            {
                '$facet': {
                    'other': [],
                    'statistics': [
                        {
                            '$set': {
                                'start_date': {
                                    '$dateFromString': {
                                        'dateString': __date_string,
                                        'timezone': '$settings.utc',
                                    }
                                }
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
                                        },
                                        {'$eq': ['$records_conv.time', None]},
                                    ]
                                }
                            }
                        },
                        {
                            '$group': {
                                '_id': None,
                                'calories': {'$sum': '$records_conv.calories'},
                                'protein': {'$sum': '$records_conv.protein'},
                                'fat': {'$sum': '$records_conv.fat'},
                                'carb': {'$sum': '$records_conv.carb'},
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
            {'$set': {'statistics': {'$first': '$statistics'}}},
            {'$unset': 'other'},
        ]
        query = [*query, *stat_query]
    answer = db_users.collection.aggregate(query)
    if answer.alive:
        return list(answer)[0]
    else:
        return None

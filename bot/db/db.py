from pymongo import MongoClient, errors, results

from config import DB_CONNECTION_STRING, DB_NAME


class Database(object):
    __client = MongoClient(host=DB_CONNECTION_STRING)

    def __init__(self, collection: str, database: str = DB_NAME):
        self.database = self.__client[database]
        self.collection = self.database[collection]

    def add_records(
        self, data: dict | list
    ) -> results.InsertOneResult | results.InsertManyResult | None:
        try:
            if isinstance(data, dict):
                return self.collection.insert_one(data)
            if len(data):
                return self.collection.insert_many(data)
            return None
        except errors.DuplicateKeyError:
            return None

    def get_records(
        self,
        *args,
        limit: int = -1,
        **kwargs,
    ):
        if limit == 1:
            return self.collection.find_one(*args, **kwargs)
        if limit > 1:
            return list(self.collection.find(*args, **kwargs))[:limit]
        if limit == -1:
            return list(self.collection.find(*args, **kwargs))

    def get_record(self, *args, **kwargs):
        return self.get_records(*args, **kwargs, limit=1)

    def update_elem(self, filter: dict, data: dict, type_: str | None = None):
        if type_ is None:
            type_ = 'set'
        self.collection.update_one(filter, {f'${type_}': data})

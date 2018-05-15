#!/usr/bin/python
#
# MongoStorage.py: stripped down version of
# https://github.com/SteemData/steemdata-mongo/blob/master/src/mongostorage.py
# by @furion

import pymongo

MONGO_HOST = 'mongod-server'
MONGO_PORT = 27017
DB_NAME = 'BeemData'

class MongoStorage(object):
    def __init__(self, db_name=DB_NAME, host=MONGO_HOST, port=MONGO_PORT):
        try:
            mongo_url = 'mongodb://%s:%s/%s' % (host, port, db_name)
            client = pymongo.MongoClient(mongo_url)
            self.db = client[db_name]

        except ConnectionFailure as e:
            print('Can not connect to MongoDB server: %s' % e)
            raise
        else:
            self.Operations = self.db['Operations']

    def list_collections(self):
        return self.db.collection_names()

    def reset_db(self):
        for col in self.list_collections():
            self.db.drop_collection(col)

    def ensure_indexes(self):
        # Operations are using _id as unique index
        self.Operations.create_index([('type', 1), ('timestamp', -1)])
        self.Operations.create_index([('block_id', 1)])
        self.Operations.create_index([('type', 1)])
        self.Operations.create_index([('block_num', -1)])
        self.Operations.create_index([('timestamp', -1)])
        # partial indexes
        self.Operations.create_index([('author', 1), ('permlink', 1)], sparse=True, background=True)
        self.Operations.create_index([('to', 1)], sparse=True, background=True)
        self.Operations.create_index([('from', 1)], sparse=True, background=True)
        self.Operations.create_index([('memo', pymongo.HASHED)], sparse=True, background=True)

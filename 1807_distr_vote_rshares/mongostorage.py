#!/usr/bin/python
# derived from @furion's SteemData code: 
# https://github.com/SteemData/steemdata-mongo/blob/master/src/mongostorage.py
import pymongo
from pymongo.errors import ConnectionFailure
import os

MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_USER = os.getenv('MONGO_USER', '')
MONGO_PASSWD = os.getenv('MONGO_PASSWD', '')
MONGO_DB = os.getenv('MONGO_DB', 'votes')


class MongoStorage(object):

    def __init__(self, db_name=MONGO_DB, host=MONGO_HOST,
                 port=MONGO_PORT, user=MONGO_USER,
                 passwd=MONGO_PASSWD):
        try:
            prefix = ''
            if user:
                prefix += user
            if passwd:
                prefix += ":%s" % (passwd)
            if user or passwd:
                prefix += "@"
            mongo_url = 'mongodb://%s%s:%s/%s' % (prefix, host, port,
                                                  db_name)
            client = pymongo.MongoClient(mongo_url)
            self.db = client[db_name]

        except ConnectionFailure as e:
            print('Can not connect to MongoDB server: %s' % e)
            raise
        else:
            self.Accounts = self.db['Accounts']

    def list_collections(self):
        return self.db.collection_names()

    def reset_db(self, col=None):
        if col is None:
            for col in self.list_collections():
                self.db.drop_collection(col)
        else:
            self.db.drop_collection(col)

    def ensure_indexes(self):
        self.Accounts.create_index([('name', 1)], unique=True)

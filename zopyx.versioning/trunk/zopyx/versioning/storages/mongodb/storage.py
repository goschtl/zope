"""
Prototype storage implementation for MongoDB
"""

import json
import pymongo

from zope.interface import implements
from zopyx.versioning.interfaces import IVersionStorage

from pymongo.connection import Connection

class MongoDBStorage(object):

    implements(IVersionStorage)

    def __init__(self, host, port, database, collection):
        self.conn = Connection(host, port)
        self.db = getattr(self.conn, database)
        self.collection = getattr(self.db, collection)

    def store(self, id, version_data, creator, comment=None):

        try:
            rev = self.collection.find({'_oid' : id}, 
                                 {'_rev' : 1} ).sort('_rev', pymongo.DESCENDING)[0]['_rev']
        except IndexError:
            rev = 0

        rev += 1 
        data = dict(_oid=id, _rev=rev)
        data.update(json.loads(version_data))
        self.collection.save(data)
        return rev



if __name__ == '__main__':

    storage = MongoDBStorage('localhost', 10200, 'zopyx-versioning', 'test')

    version_data = json.dumps({'id' : '42', 'text' : 'blather' })
    for i in range(1000):
        print storage.store('42', version_data, 'ajung', 'versioning test')




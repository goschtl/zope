"""
Prototype storage implementation for MongoDB
"""

from pymongo.connection import Connection

from cjson import encode as json_encode
from cjson import decode as json_decode

from zope.interface import implements
from zopyx.versioning.interfaces import IVersionStorage
from zopyx.versioning import errors


class MongoDBStorage(object):

    implements(IVersionStorage)

    def __init__(self, host, port, database):
        self.conn = Connection(host, port)
        self.db = getattr(self.conn, database)
        self.metadata = self.db.metadata
        self.revisions = self.db.revisions

    def clear(self):
        self.metadata.remove()
        self.revisions.remove()

    def store(self, id, version_data, creator, comment=None):

        id_entry = self.metadata.find_one({'_oid' : id})
        if id_entry is None:
            revision = 0
            self.metadata.save({'_oid' : id, '_rev' : 0})
        else:
            revision = id_entry['_rev'] + 1
            self.metadata.update({'_oid' : id}, {'$set' : {'_rev' : revision}} )

        data = dict(_oid=id, _rev=revision)
        data.update(json_decode(version_data))
        self.revisions.save(data)
        return revision

    def retrieve(self, id, revision):

        count = self.revisions.find({'_oid' : id}).count()
        if count == 0:
            raise errors.NoDocumentFound('No document with ID %s found' % id)

        entry = self.revisions.find_one({'_oid' : id, '_rev' : revision})
        if entry:
            del entry['_oid']
            del entry['_rev']
            del entry['_id']
            return json_encode(entry)

        raise errors.NoRevisionFound('No revision %d found for document with ID %s found' % (revision, id))

    def remove(self, id):
        if self.revisions.find({'_oid' : id}).count() == 0:
            raise errors.NoDocumentFound('No document with ID %s found' % id)
        self.metadata.remove({'_oid' : id})
        self.revisions.remove({'_oid' : id})

    def has_revision(self, id, revision):
        return bool(self.revisions.find_one({'_oid' : id, '_rev' : revision}))

    def list_revisions(self, id):
        if self.revisions.find({'_oid' : id}).count() == 0:
            raise errors.NoDocumentFound('No document with ID %s found' % id)

        revisions = self.revisions.find({'_oid' : id})
        if revisions.count == 0:
            raise errors.NoDocumentFound('No document with ID %s found' % id)
        return sorted([r['_rev'] for r in revisions])

    def remove_revision(self, id, revision):
        if self.revisions.find({'_oid' : id}).count() == 0:
            raise errors.NoDocumentFound('No document with ID %s found' % id)
        self.revisions.remove({'_oid' : id, '_rev' : revision})


if __name__ == '__main__':

    storage = MongoDBStorage('localhost', 10200, 'zopyx-versioning')

    storage.remove('42')
    for i in range(10):
        version_data = json.dumps({'id' : '42', 'text' : 'blather-%d' % i})
        print storage.store('42', version_data, 'ajung', 'versioning test')
    print storage.retrieve('42', 9)
    print storage.has_revision('42', 9)
    print storage.has_revision('42', 42)

    print storage.list_revisions('42')
    storage.remove_revision('42', 9)
    print storage.store('42', version_data, 'ajung', 'versioning test')
    print storage.list_revisions('42')

################################################################
# zopyx.versioning
# (C) 2010, ZOPYX Ltd, D-72070 Tuebingen
# Published under the Zope Public License 2.1
################################################################

"""
Prototype storage implementation for MongoDB
"""

import anyjson
from datetime import datetime
from pymongo.connection import Connection

from zope.interface import implements
from zopyx.versioning import errors
from zopyx.versioning.interfaces import IVersionStorage

class MongoDBStorage(object):

    implements(IVersionStorage)

    def __init__(self, host, port, database):
        self.conn = Connection(host, port)
        self.db = getattr(self.conn, database)
        self.metadata = self.db.metadata
        self.revisions = self.db.revisions

    def __del__(self):
        self.conn.end_request()

    def clear(self):
        self.metadata.remove()
        self.revisions.remove()

    def store(self, id, version_data, revision_metadata):
        id_entry = self.metadata.find_one({'_oid' : id})
        if id_entry is None:
            revision = 0
            self.metadata.save({'_oid' : id, '_rev' : 0})
        else:
            revision = id_entry['_rev'] + 1
            self.metadata.update({'_oid' : id}, 
                                 {'$set' : {'_rev' : revision}} )

        revision_metadata = anyjson.deserialize(revision_metadata)
        revision_metadata['created'] = datetime.utcnow().isoformat()
        data = dict(_oid=id, 
                    _rev=revision,
                    _data=anyjson.deserialize(version_data),
                    _metadata=revision_metadata,
                    )
        self.revisions.save(data)
        return revision

    def retrieve(self, id, revision):
        count = self.revisions.find({'_oid' : id}).count()
        if count == 0:
            raise errors.NoDocumentFound('No document with ID %s found' % id)
        entry = self.revisions.find_one({'_oid' : id, '_rev' : revision})
        if entry:
            return anyjson.serialize(entry['_data'])
        raise errors.NoRevisionFound('No revision %d found for document '
                                     'with ID %s found' % (revision, id))

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

    def revision_metadata(self, id, revision):
        revision = self.revisions.find_one({'_oid' : id, '_rev' : revision})
        return revision['_metadata']

    def remove_revision(self, id, revision):
        if self.revisions.find({'_oid' : id}).count() == 0:
            raise errors.NoDocumentFound('No document with ID %s found' % id)
        self.revisions.remove({'_oid' : id, '_rev' : revision})


if __name__ == '__main__':

    storage = MongoDBStorage('localhost', 10200, 'zopyx-versioning')

    storage.remove('42')
    for i in range(10):
        version_data = anyjson.serialize({'id' : '42', 'text' : 'blather-%d' % i})
        print storage.store('42', version_data, 'ajung', 'versioning test')
    print storage.retrieve('42', 9)
    print storage.has_revision('42', 9)
    print storage.has_revision('42', 42)

    print storage.list_revisions('42')
    storage.remove_revision('42', 9)
    print storage.store('42', version_data, 'ajung', 'versioning test')
    print storage.list_revisions('42')

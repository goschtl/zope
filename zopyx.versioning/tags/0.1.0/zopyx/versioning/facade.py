################################################################
# zopyx.versioning
# (C) 2010, ZOPYX Ltd, D-72070 Tuebingen
# Published under the Zope Public License 2.1
################################################################

import riparse
from zope.interface import implements
from interfaces import IVersioning

class VersioningFacade(object):

    implements(IVersioning)

    def getStorage(self, dsn):

        r = riparse.parse(dsn)
        if r['scheme'] == 'mongo':
            from zopyx.versioning.storages.mongodb.storage import MongoDBStorage
            return MongoDBStorage(host=r['host'],
                                  port=int(r['port']),
                                  database=r['path'][0])

        raise ValueError('Unsupported schema: %s' % r['scheme'])


if __name__ == '__main__':
    print VersioningFacade().getStorage('mongo://localhost:10200/foo')
    print VersioningFacade().getStorage('zodb://localhost:10200/foo')

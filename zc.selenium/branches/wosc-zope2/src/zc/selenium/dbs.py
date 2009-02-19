##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Demo storage push/pop operations.

$Id: dbs.py 12602 2006-07-06 06:29:48Z fred $
"""
from ZODB.DemoStorage import DemoStorage
from ZODB.DB import DB

ALLOWED_STORAGES = [DemoStorage]

# zope2 compatibility
try:
    from tempstorage.TemporaryStorage import TemporaryStorage
    ALLOWED_STORAGES.append(TemporaryStorage)
except ImportError:
    pass


class DatabaseAware(object):
    def get_db(self):
        try:
            import Zope2
            DB = Zope2.DB
        except ImportError:
            DB = self.request.publication.db
        return DB

    def set_db(self, db):
        try:
            import Zope2
            Zope2.DB = db
        except ImportError:
            self.request.publication.db = db
        return DB

    db = property(get_db, set_db)

    def is_demo_db(self):
        for db in self.db.databases.values():
            if not self.is_demo_storage(db._storage):
                return False
        return True

    def is_demo_storage(self, storage):
        for class_ in ALLOWED_STORAGES:
            if isinstance(storage, class_):
                return True
        return False


class PushDBs(DatabaseAware):
    """Push DB"""

    def __call__(self):
        if not self.is_demo_db():
            raise RuntimeError("Wrong mode")

        databases = {}
        for name, db in self.db.databases.items():
            DB(DemoStorage(base=db._storage),
               databases=databases, database_name=name,
               )

        newdb = databases[self.db.database_name]
        newdb.pushed_base = self.db # hacking extra attr onto db
        self.db = newdb

        return 'Done'


class PopDBs(DatabaseAware):
    """Pop DB"""

    def __call__(self):
        self.db = self.db.pushed_base
        return 'Done'

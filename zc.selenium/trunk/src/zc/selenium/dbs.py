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
"""Demo storage push/pop operations, as resources.

$Id: dbs.py 12602 2006-07-06 06:29:48Z fred $
"""

from ZODB.DemoStorage import DemoStorage
from ZODB.DB import DB
from zope.exceptions.interfaces import UserError

import zc.selenium.resource


class PushDBs(zc.selenium.resource.ResourceBase):

    def GET(self):
        publication = self.request.publication
        if [1
            for d in publication.db.databases.values()
            if not isinstance(d._storage, DemoStorage)
            ]:
            raise UserError("Wrong mode")

        databases = {}
        for name, db in publication.db.databases.items():
            DB(DemoStorage(base=db._storage),
               databases=databases, database_name=name,
               )

        newdb = databases[publication.db.database_name]
        newdb.pushed_base = publication.db # hacking extra attr onto db
        publication.db = newdb

        return 'Done'

class PopDBs(zc.selenium.resource.ResourceBase):

    def GET(self):
        publication = self.request.publication
        publication.db = publication.db.pushed_base

        return 'Done'

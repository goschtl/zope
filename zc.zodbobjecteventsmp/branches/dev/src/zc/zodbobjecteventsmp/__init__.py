##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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

# Monkey-patch that provides tracking of object modifications

def patch(db, func):
    """Monkey patch a database to call the given function.

    When invalidations occur, the fnction will be called with a tid
    and list of oids.
    """
    original = db.invalidate
    def invalidate(tid, oids, connection=None, version=''):
        original(tid, oids, connection, version)
        func(tid, oids)
    db.invalidate = invalidate

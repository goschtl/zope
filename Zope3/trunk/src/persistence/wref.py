##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ZODB-based persistent weakrefs

$Id: wref.py,v 1.1 2004/01/06 19:50:38 jim Exp $
"""

WeakRefMarker = object()

class WeakRef(object):
    """Persistent weak references

    Persistent weak references are used much like Python weak references.
    The major difference is that you can't (at least not currently)
    specify an object to be called when the object is removed from the
    database.

    Here's an example:

    >>> import persistence.list
    >>> import zodb.tests.util
    >>> ob = persistence.list.PersistentList()
    >>> ref = WeakRef(ob)
    >>> ref() is ob
    True

    >>> db = zodb.tests.util.DB()
    
    >>> conn1 = db.open()
    >>> conn1.root()['ob'] = ob
    >>> conn1.root()['ref'] = ref
    >>> zodb.tests.util.commit()

    >>> conn2 = db.open()
    >>> conn1.root()['ref']() is conn1.root()['ob']
    True

    >>> del conn1.root()['ob']
    >>> zodb.tests.util.commit()
    >>> zodb.tests.util.pack(db)

    >>> conn3 = db.open()
    >>> conn3.root()['ref']()
    >>> conn3.root()['ob']
    Traceback (most recent call last):
    ...
    KeyError: 'ob'

    >>> db.close()
    """

    # We set _p_oid to a merker so that the serialization system can
    # provide special handling of weakrefs.
    _p_oid = WeakRefMarker

    def __init__(self, ob):
        self._v_ob = ob
        self.oid = ob._p_oid
        self.dm = ob._p_jar

    def __call__(self):
        try:
            return self._v_ob
        except AttributeError:
            try:
                self._v_ob = self.dm.get(self.oid)
            except KeyError:
                return None
            return self._v_ob
            

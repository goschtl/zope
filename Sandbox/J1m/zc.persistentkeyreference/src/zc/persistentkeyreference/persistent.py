##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""KeyReference for persistent objects.

Provides an IKeyReference adapter for persistent objects.
"""
from ZODB.interfaces import IConnection
from ZODB.ConflictResolution import PersistentReference
import zope.interface

import zope.keyreference.interfaces
import zope.keyreference.persistent

class KeyReferenceToPersistent(
    zope.keyreference.persistent.KeyReferenceToPersistent):

    key_type_id = 'zc.persistentkeyreference'

    def __cmp__(self, other):
        if self.key_type_id == other.key_type_id:
            # While it makes subclassing this class inconvenient,
            # comparing the object's type is faster than doing an
            # isinstance check.  The intent of using type instead
            # of isinstance is to avoid loading state just to
            # determine if we're in conflict resolution.
            if type(self.object) is PersistentReference:
                # We are doing conflict resolution.
                assert isinstance(other.object, PersistentReference), (
                    'other object claims to be '
                    'zope.app.keyreference.persistent but, during conflict '
                    'resolution, object is not a PersistentReference')
                self_name = self.object.database_name
                other_name = other.object.database_name
                if (self_name is None) ^ (other_name is None):
                    # one of the two database_names are None during conflict
                    # resolution.  At this time the database_name is
                    # inaccessible, not unset (it is the same database as the
                    # object being resolved).  If they were both None, we
                    # would know they are from the same database, so we can
                    # compare the oids.  If neither were None, we would be
                    # able to reliably compare.  However, in this case,
                    # one is None and the other is not, so we can't know how
                    # they would sort outside of conflict resolution.  Give
                    # up.
                    raise ValueError('cannot sort reliably')
                self_oid = self.object.oid
                other_oid = other.object.oid
            else:
                self_name = self.object._p_jar.db().database_name
                self_oid = self.object._p_oid
                other_name = other.object._p_jar.db().database_name
                other_oid = other.object._p_oid
            return cmp((self_name, self_oid), (other_name, other_oid))

        return cmp(self.key_type_id, other.key_type_id)

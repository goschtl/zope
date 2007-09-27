##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Fixup missing oids by copying them froma backup.

XXX untested
"""

import ZODB.POSException
import ZODB.serialize
import transaction()

def fixup_what(oids, src, dest, result=None, seen=None):
    if result is None:
        result = []
        seen = {}

    for oid in oids:
        if oid in seen:
            continue
        seen[oid] = 1

        # See if it is already in the dest:                                     
        try:
            dest.load(oid, '')
        except ZODB.POSException.POSKeyError:
            pass
        else:
            # Already there. Skip                                               
            continue

        pickle, s = src.load(oid, '')
        result.append((oid, pickle))
        fixup_what(ZODB.serialize.referencesf(pickle), src, dest,
                   result, seen)

    return result

def fixup(oids, src, dest):
    t = transaction.begin()
    dest.tpc_begin(t)
    for oid, pickle in fixup_what(oids, src, dest):
        dest.store(oid, '\0'*8, pickle, '', t)
    dest.tpc_vote(t)
    dest.tpc_finish(t)

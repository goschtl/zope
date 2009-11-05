##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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

from ZODB.DB import DB
import cStringIO
import ZODB.broken
import ZODB.utils
import logging
import pickle
import pickletools
import sys
import transaction
import zodbupdate.serialize

logger = logging.getLogger('zodbupdate')


class Updater(object):
    """Update class references for all current objects in a storage."""

    def __init__(self, storage, dry=False, renames=None):
        self.dry = dry
        self.storage = storage
        self.update = zodbupdate.serialize.ObjectRenamer(renames or {})

    def __call__(self):
        t = transaction.Transaction()
        self.storage.tpc_begin(t)
        t.note('Updated factory references using `zodbupdate`.')

        for oid, serial, current in self.records:
            new = self.update.rename(current)
            if new is None:
                continue
            logger.debug('Updated %s' % ZODB.utils.oid_repr(oid))
            self.storage.store(oid, serial, new.getvalue(), '', t)

        if self.dry:
            logger.info('Dry run selected, aborting transaction.')
            self.storage.tpc_abort(t)
        else:
            logger.info('Committing changes.')
            self.storage.tpc_vote(t)
            self.storage.tpc_finish(t)

    @property
    def records(self):
        next = None
        while True:
            oid, tid, data, next = self.storage.record_iternext(next)
            yield oid, tid, cStringIO.StringIO(data)
            if next is None:
                break


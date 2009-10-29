##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

from zc.catalogqueue.CatalogEventQueue import REMOVED, CHANGED, ADDED

import BTrees.Length
import datetime
import logging
import persistent
import pytz
import zc.catalogqueue.CatalogEventQueue
import zc.catalogqueue.interfaces
import zope.interface

logger = logging.getLogger(__name__)


class CatalogQueue(persistent.Persistent):

    zope.interface.implements(zc.catalogqueue.interfaces.ICatalogQueue)

    lastProcessedTime = None
    totalProcessed = 0

    def __init__(self, buckets=1009):
        self._buckets = buckets
        self._queues = [
            zc.catalogqueue.CatalogEventQueue.CatalogEventQueue()
            for i in range(buckets)
            ]

    def __len__(self):
        try:
            return self._length()
        except AttributeError:
            return 0

    def _change_length(self, change):
        try:
            length = self._length
        except AttributeError:
            length = self._length = BTrees.Length.Length()
            change = 0
            for queue in self._queues:
                change += len(queue)

        length.change(change)

    def _notify(self, id, event):
        self._change_length(
            self._queues[hash(id) % self._buckets].update(id, event))

    def add(self, id):
        self._notify(id, ADDED)

    def update(self, id):
        self._notify(id, CHANGED)

    def remove(self, id):
        self._notify(id, REMOVED)

    def process(self, ids, catalogs, limit):
        done = 0
        for queue in self._queues:
            for id, (_, event) in queue.process(limit-done).iteritems():
                if event is REMOVED:
                    for catalog in catalogs:
                        catalog.unindex_doc(id)
                else:
                    ob = ids.queryObject(id)
                    if ob is None:
                        logger.warn("Couldn't find object for %s", id)
                    else:
                        for catalog in catalogs:
                            catalog.index_doc(id, ob)
                done += 1
                self._change_length(-1)

            if done >= limit:
                break

        self.lastProcessedTime = datetime.datetime.now(pytz.UTC)
        self.totalProcessed += done

        return done

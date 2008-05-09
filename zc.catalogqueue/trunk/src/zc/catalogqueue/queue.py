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

    _buckets = 1009 # Maybe configurable someday

    def __init__(self):
        self._queues = [
            zc.catalogqueue.CatalogEventQueue.CatalogEventQueue()
            for i in range(self._buckets)
            ]

    def _notify(self, id, event):
        self._queues[hash(id) % self._buckets].update(id, event)

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

            if done >= limit:
                break

        self.lastProcessedTime = datetime.datetime.now(pytz.UTC)
        self.totalProcessed += done

        return done

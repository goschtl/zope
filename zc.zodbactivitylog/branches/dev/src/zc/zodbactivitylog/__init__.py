##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""ZODB Activity Monitor that Just logs

This is somewhat of a temporary hack.  ZODB should really generate events.
Then we could do this as an event subscriber.

Unfortunately, this is complicated by the api for getting connection
statitics. This really needs to get cleaned up.

$Id$
"""

import logging

logger = logging.getLogger(__name__)

class ActivityMonitor:

    def __init__(self, base=None):
        self._base = base

    def closedConnection(self, conn):
        loads, stores = conn.getTransferCounts(False)
        if self._base is not None:
            self._base.closedConnection(conn)
        conn.getTransferCounts(True) # Make sure connection counts are cleared
        logger.info("%s %s", loads, stores)

    def __getattr__(self, name):
        return getattr(self._base, name)


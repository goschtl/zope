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
"""Zope 3 setup support
"""

import ZODB.interfaces
import zope.component
import zc.zodbactivitylog
import zope.app.appsetup.interfaces


@zope.component.adapter(zope.app.appsetup.interfaces.IDatabaseOpenedEvent)
def register(opened_event):
    for name, db in zope.component.getUtilitiesFor(ZODB.interfaces.IDatabase):
        db.setActivityMonitor(
            zc.zodbactivitylog.ActivityMonitor(db.getActivityMonitor())
            )

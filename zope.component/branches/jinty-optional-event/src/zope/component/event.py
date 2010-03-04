##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Implement Component Architecture-specific event dispatching, based
on subscription adapters / handlers.

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.component.interfaces
from zope.component._event import subscribers, notify

def dispatch(*event):
    zope.component.subscribers(event, None)

subscribers.append(dispatch)


@zope.component.adapter(zope.component.interfaces.IObjectEvent)
def objectEventNotify(event):
    """Event subscriber to dispatch ObjectEvents to interested adapters."""
    zope.component.subscribers((event.object, event), None)

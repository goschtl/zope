##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""

from zope.component import subscribers
from zope.app.event.objectevent import Attributes
from zope.app.event.objectevent import ObjectModifiedEvent

from zope.generic.directlyprovides import IProvides
from zope.generic.directlyprovides import IObjectModifiedEventDispatchingProvides



def notifyObjectModifiedEvent(event):
    
    if IObjectModifiedEventDispatchingProvides.providedBy(event.object):
        event = ObjectModifiedEvent(event.object, Attributes(IProvides, '__provides__'))

        for ignored in subscribers((event,), None):
            pass

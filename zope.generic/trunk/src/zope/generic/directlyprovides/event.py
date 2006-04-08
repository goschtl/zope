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

__docformat__ = 'restructuredtext'

from zope.interface import implements

from zope.generic.directlyprovides import IDirectlyProvidesModifiedEvent



class DirectlyProvidesModifiedEvent(object):
    """Directly provides event.

    Event with two marker types:

        >>> obj = object()
        >>> event = DirectlyProvidesModifiedEvent(obj)

        >>> event.object is obj
        True
    
        >>> IDirectlyProvidesModifiedEvent.providedBy(event)
        True

    """

    implements(IDirectlyProvidesModifiedEvent)

    def __init__(self, object):
        self.object = object

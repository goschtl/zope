##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Define view component for event service control.

$Id$
"""
from zope.app.event.interfaces import IEventService

class Control:
    __used_for__ = IEventService

    # XXX: Really needed? Currently it does nothing (obviously). I guess it is
    # just a placeholder for later functionality.

    # This view should be responsible to display all the objects that are
    # subscribed to it and maybe even a log of the last events it handeled.

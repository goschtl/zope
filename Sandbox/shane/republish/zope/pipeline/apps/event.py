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

from zope.event import notify
from zope.interface import adapts
from zope.interface import implements
from zope.publisher.interfaces import IWSGIApplication
from zope.publisher.interfaces.event import BeforeTraverseEvent
from zope.publisher.interfaces.event import EndRequestEvent


class EventNotifier(object):
    """Fires request-related events.

    Fires BeforeTraverseEvent and EndRequestEvent at the appropriate
    times.
    """
    implements(IWSGIApplication)
    adapts(IWSGIApplication)

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = environ['zope.request']
        request.traversal_hooks.append(fireBeforeTraverse)
        try:
            return self.app(environ, start_response)
        finally:
            if request.traversed:
                name, ob = request.traversed[-1]
            else:
                ob = None
            notify(EndRequestEvent(ob, request))

def fireBeforeTraverse(request, ob):
    notify(BeforeTraverseEvent(ob, request))

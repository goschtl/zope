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
from zope.interface import implements
from zope.publisher.interfaces import IWSGIApplication
from zope.publisher.interfaces.event import BeforeTraverseEvent
from zope.publisher.interfaces.event import EndRequestEvent

from zope.pipeline.envkeys import TRAVERSAL_HOOKS_KEY
from zope.pipeline.envkeys import TRAVERSED_KEY


class EventNotifier(object):
    """Fires request-related events.

    Adds a traversal hook to the environment. Fires BeforeTraverseEvent
    and EndRequestEvent at the appropriate times. Requires the
    'zope.pipeline.traversed' key for firing events.
    """
    implements(IWSGIApplication)

    def __init__(self, next_app):
        self.next_app = next_app

    def __call__(self, environ, start_response):
        hooks = environ.setdefault(TRAVERSAL_HOOKS_KEY, [])
        hooks.append(fire_before_traverse)
        try:
            return self.next_app(environ, start_response)
        finally:
            traversed = environ.get(TRAVERSED_KEY)
            if traversed:
                name, ob = traversed[-1]
            else:
                ob = None
            notify(EndRequestEvent(ob, request))

def fire_before_traverse(request, ob):
    notify(BeforeTraverseEvent(ob, request))

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
"""Principal Factory Plugin

$Id$
"""
__docformat__ = "reStructuredText"
from persistent import Persistent

from zope.event import notify
from zope.interface import implements

from zope.app.container.contained import Contained
import interfaces

class Principal:
    """A simple Principal

    >>> p = Principal(1)
    >>> p
    Principal(1)
    >>> p.id
    1

    >>> p = Principal('foo')
    >>> p
    Principal('foo')
    >>> p.id
    'foo'
    """
    
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return 'Principal(%r)' %self.id


class PrincipalFactory(Persistent, Contained):
    """A simple principal factory.

    First we need to register a simple subscriber that records all events.

    >>> events = []
    >>> import zope.event
    >>> zope.event.subscribers.append(events.append)

    Now we create a principal factory and try to create the principals.

    >>> from zope.publisher.browser import TestRequest
    >>> pf = PrincipalFactory()

    >>> principal = pf.createAuthenticatedPrincipal(1, {}, TestRequest())
    >>> principal.id
    1
    >>> event = events[0]
    >>> isinstance(event, interfaces.AuthenticatedPrincipalCreated)
    True
    >>> event.principal is principal
    True
    >>> event.info
    {}

    >>> principal = pf.createFoundPrincipal(2, {})
    >>> principal.id
    2
    >>> event = events[1]
    >>> isinstance(event, interfaces.FoundPrincipalCreated)
    True
    >>> event.principal is principal
    True
    >>> event.info
    {}
    """
    implements(interfaces.IPrincipalFactoryPlugin)           

    def createAuthenticatedPrincipal(self, id, info, request):
        """See zope.app.pas.interfaces.IPrincipalFactoryPlugin"""
        principal = Principal(id)
        notify(interfaces.AuthenticatedPrincipalCreated(principal,
                                                        info, request))
        return principal


    def createFoundPrincipal(self, id, info):
        """See zope.app.pas.interfaces.IPrincipalFactoryPlugin"""
        principal = Principal(id)
        notify(interfaces.FoundPrincipalCreated(principal, info))
        return principal

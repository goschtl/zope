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

from zope.event import notify
from zope.interface import implements

from zope.app.security.interfaces import IPrincipal

from zope.app.pas import interfaces

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
    implements(IPrincipal)

    title = description = u''
    
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return 'Principal(%r)' %self.id


class PrincipalFactory:
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

def addTitleAndDescription(event):
    """Set title and description from info

    We can set title and description information for principals if keys
    can be found in the info:

      >>> principal = Principal('3')
      >>> event = interfaces.FoundPrincipalCreated(
      ...    principal, {'title': u'Bob', 'description': u'Eek'})
      >>> addTitleAndDescription(event)
      
      >>> principal.title
      u'Bob'
      >>> principal.description
      u'Eek'

    Note that the attributes are only set if they aren't set already:  

      >>> event = interfaces.FoundPrincipalCreated(
      ...    principal, {'title': u'Fred', 'description': u'Dude'})
      >>> addTitleAndDescription(event)
      
      >>> principal.title
      u'Bob'
      >>> principal.description
      u'Eek'

    """

    principal = event.principal
    info = event.info

    title = info.get('title')
    if title and not principal.title:
        principal.title = title

    description = info.get('description')
    if description and not principal.description:
        principal.description = description

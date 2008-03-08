##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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

import zope.interface
import zope.component
from zope.publisher.interfaces import IRequest
from zope.app.session.interfaces import IClientId
from zope.app.session.interfaces import IClientIdManager
from zope.app.session.session import PersistentSessionDataContainer
from zope.app.session.session import Session
from z3c.authentication.cookie import interfaces


class LifeTimeClientId(str):
    """Client browser id for LifeTimeSession.

    >>> from z3c.authentication.cookie import testing
    >>> request = testing.clientIdSetUp()

    >>> id1 = LifeTimeClientId(request)
    >>> id2 = LifeTimeClientId(request)
    >>> id1 == id2
    True

    >>> testing.clientIdTearDown()

    """
    zope.interface.implements(interfaces.ILifeTimeClientId)
    zope.component.adapts(IRequest)

    def __new__(cls, request):
        name = 'LifeTimeSessionClientIdManager'
        util = zope.component.getUtility(IClientIdManager, name=name)
        id = util.getClientId(request)
        return str.__new__(cls, id)


class LifeTimeSession(Session):
    """Session valid over a long time.
    
    Note this session requires a IClientIdManager configured with a 
    ``cookieLifetime = 0`` registered as a named utility with a 
    ``name = LifeTimeSessionClientIdManager``.
    """
    zope.interface.implements(interfaces.ILifeTimeSession)
    zope.component.adapts(IRequest)

    def __init__(self, request):
        self.client_id = str(interfaces.ILifeTimeClientId(request))


class CookieCredentialSessionDataContainer(PersistentSessionDataContainer):
    """A persistent cookie credential container."""

    zope.interface.implements(
        interfaces.ICookieCredentialSessionDataContainer)

    def __init__(self):
        super(CookieCredentialSessionDataContainer, self).__init__()
        self.timeout = 1 * 60 * 60 * 24 * 365

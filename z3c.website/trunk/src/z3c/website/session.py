##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 69382 2006-08-09 13:26:53Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.schema.fieldproperty import FieldProperty
from zope.publisher.interfaces import IRequest
import zope.security.management
import zope.security.interfaces
from zope.app.session import session

from z3c.website import interfaces

SESSION_KEY = 'z3c.website.interfaces.IDemoSession'


def getRequest():
    try:
        i = zope.security.management.getInteraction() # raises NoInteraction
    except zope.security.interfaces.NoInteraction:
        return

    for p in i.participations:
        if IRequest.providedBy(p):
            return p


class SessionData(object):
    """None persistent sample content object for storing in a session."""

    zope.interface.implements(interfaces.ISessionData)

    content = FieldProperty(interfaces.ISessionData['content'])


class DemoSession(session.Session):
    """Simply session which knows how to set and get a object."""

    zope.interface.implements(interfaces.IDemoSession)

    def setObject(self, key, obj):
        """Add a object to the session."""
        spd = self.__getitem__(SESSION_KEY)
        spd[key] = obj

    def getObject(self, key, default=None):
        spd = self.__getitem__(SESSION_KEY)
        return spd.get(key, default)


def getSessionData(form):
    """Kows how to setup a object for a form and store it in a session.
    
    The form must provide a class under the attribute contentFactory.
    """
    key = form.__class__.__name__
    request = getRequest()
    if request is None:
        raise KeyError("Bad setup, there is no interaction for form %s" % key)
    session = interfaces.IDemoSession(request)
    obj = session.getObject(key)
    if obj is None:
        factory = form.getContentFactory()
        if hasattr(factory, '__call__'):
            obj = factory()
        else:
            # we get a dict
            obj = factory
        session.setObject(key, obj)
    return obj

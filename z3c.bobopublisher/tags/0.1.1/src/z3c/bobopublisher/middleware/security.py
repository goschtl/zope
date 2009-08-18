##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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
$Id: middleware.py 102811 2009-08-15 15:20:10Z kobold $
"""

from zope.interface import implements
from zope.security.interfaces import IPrincipal, IParticipation
from zope.security.management import newInteraction, endInteraction


class Participation(object):
    """Participation object
    
    Verify the class:

        >>> from zope.interface.verify import verifyClass
        >>> verifyClass(IParticipation, Participation)
        True
    
    Verify the object:

        >>> from zope.interface.verify import verifyObject
        >>> obj = Participation(None)
        >>> verifyObject(IParticipation, obj)
        True
 
    """

    implements(IParticipation)

    def __init__(self, principal):
        self.principal = principal
        self.interaction = None


class SecurityMiddleware(object):
    """WSGI middleware for integration with zope.security"""

    def __init__(self, app, key):
        self.app = app
        self.key = key

    def __call__(self, environ, start_response):
        principal = IPrincipal(environ.get(self.key))
        newInteraction(Participation(principal))
        result = self.app(environ, start_response)
        endInteraction()
        return result


def make_security_middleware(app, global_conf, key):
    """Configure a ProxyMiddleware middleware"""
    return SecurityMiddleware(app, key)

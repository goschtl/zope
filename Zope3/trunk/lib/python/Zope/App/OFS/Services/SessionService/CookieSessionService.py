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

"""Simplistic session service implemented using cookies.

This is more of a demonstration than a full implementation, but it should
work.
"""

# System imports
import sha, time, string, random

# Zope3 imports
from Persistence import Persistent
from Persistence.PersistentDict import PersistentDict
from Zope.Server.HTTP.http_date import build_http_date

# Sibling imports
from ISessions import ISessionService, IConfigureSessionService


cookieSafeTrans = string.maketrans("+/", "-.")


class CookieSessionService(Persistent):
    """Session service implemented using cookies."""

    __implements__ = Persistent.__implements__, ISessionService, IConfigureSessionService
    
    def __init__(self):
        self.dataManagers = PersistentDict()
        self.namespace = "zope3-cs-%x" % (int(time.time()) - 1000000000)
    
    def generateUniqueId(self):
        """Generate a new, random, unique id."""
        data = "%.20f%.20f%.20f" % (random.random(), time.time(), time.clock())
        digest = sha.sha(data).digest()
        return digest.encode("base64")[:-2].translate(cookieSafeTrans)

    def getRequestId(self, request):
        """Return the sessionId encoded in request or None if it's non-existent."""
        sid = request.cookies.get(self.namespace)
        if sid is None or len(sid) != 27:
            return None
        else:
            return sid

    def setRequestId(self, request, id):
        """Set cookie with id on request."""
        request.response.setCookie(self.namespace, id, expires=build_http_date(time.time() + 1800))
    

    #####################################
    # Implementation of ISessionService #
    
    def getSessionId(self, request):
        sid = self.getRequestId(request)
        if sid is None:
            sid = self.generateUniqueId()
        self.setRequestId(request, sid)
        return sid

    def invalidate(self, sessionId):
        for d in self.dataManagers.values():
            d.deleteData(sessionId)

    def getDataManager(self, name):
        return self.dataManagers[name]

    def registerDataManager(self, name, dataManager):
        if self.dataManagers.has_key(name):
            raise ValueError, "DataManager already registered with name %r" % name
        self.dataManagers[name] = dataManager

    def unregisterDataManager(self, name):
        del self.dataManagers[name]

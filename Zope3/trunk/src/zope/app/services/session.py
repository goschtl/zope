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
import sha, time, string, random, hmac

# Zope3 imports
from persistence import Persistent
from persistence.dict import PersistentDict
from zope.server.http.http_date import build_http_date
from zope.component import getService

# Sibling imports
from zope.app.interfaces.services.session import ISessionService
from zope.app.interfaces.services.session import IConfigureSessionService


cookieSafeTrans = string.maketrans("+/", "-.")

def digestEncode(s):
    """Encode SHA digest for cookie."""
    return s.encode("base64")[:-2].translate(cookieSafeTrans)


class CookieSessionService(Persistent):
    """Session service implemented using cookies."""

    __implements__ = (Persistent.__implements__, ISessionService,
                      IConfigureSessionService)

    def __init__(self):
        self.dataManagers = PersistentDict()
        self.namespace = "zope3-cs-%x" % (int(time.time()) - 1000000000)
        self.secret = "%.20f" % random.random()
        self.cookieLifeSeconds = 1800

    def generateUniqueId(self):
        """Generate a new, random, unique id."""
        data = "%.20f%.20f%.20f" % (random.random(), time.time(), time.clock())
        digest = sha.sha(data).digest()
        s = digestEncode(digest)
        # we store a HMAC of the random value together with it, which makes
        # our session ids unforgeable.
        mac = hmac.new(s, self.secret, digestmod=sha).digest()
        return s + digestEncode(mac)

    def getRequestId(self, request):
        """Return the sessionId encoded in request or None if it's
        non-existent."""
        # If there is an id set on the response, use that but don't trust it.
        # We need to check the response in case there has already been a new
        # session created during the course of this request.
        response_cookie = request.response.getCookie(self.namespace)
        if response_cookie:
            sid = response_cookie['value']
        else:
            sid = request.cookies.get(self.namespace)
        if sid is None or len(sid) != 54:
            return None
        s, mac = sid[:27], sid[27:]
        if (digestEncode(hmac.new(s, self.secret, digestmod=sha).digest())
            != mac):
            return None
        else:
            return sid

    def setRequestId(self, request, id):
        """Set cookie with id on request."""
        # XXX Currently, the path is the ApplicationURL. This is reasonable,
        #     and will be adequate for most purposes.
        #     A better path to use would be that of the folder that contains
        #     the service-manager this service is registered within. However,
        #     that would be expensive to look up on each request, and would
        #     have to be altered to take virtual hosting into account.
        #     Seeing as this service instance has a unique namespace for its
        #     cookie, using ApplicationURL shouldn't be a problem.
        if self.cookieLifeSeconds:
            expires = build_http_date(time.time() + self.cookieLifeSeconds)
        else:
            expires = None
        request.response.setCookie(
                self.namespace,
                id,
                expires=expires,
                path=request.getApplicationURL(path_only=True)
                )


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
            raise ValueError(
                    "DataManager already registered with name %r" % name)
        self.dataManagers[name] = dataManager

    def unregisterDataManager(self, name):
        del self.dataManagers[name]


def getSessionDataObject(context, request, name):
    """Get data object from appropriate ISessionDataManager."""
    service = getService(context, "Sessions")
    sid = service.getSessionId(request)
    return service.getDataManager(name).getDataObject(sid)

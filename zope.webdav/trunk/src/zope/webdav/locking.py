##############################################################################
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""WebDAV LOCK and UNLOCK methods.

Request contains a lockinfo XML element.

  <!ELEMENT lockinfo (lockscope, locktype, owner?)  >
  <!ELEMENT lockscope (exclusive | shared) >
  <!ELEMENT locktype (write) >
  <!ELEMENT shared EMPTY >
  <!ELEMENT exclusive EMPTY >
  <!ELEMENT write EMPTY >
  <!ELEMENT owner ANY >

Response contains a lockdiscovery XML element.

  <!ELEMENT lockdiscovery (activelock)* >
  <!ELEMENT activelock (lockscope, locktype, depth, owner?, timeout?,
            locktoken?, lockroot)>
  <!ELEMENT depth (#PCDATA) >
     "0" | "1" | "infinity"
  <!ELEMENT timeout (#PCDATA) >
    TimeType (defined in Section 10.7).
  <!ELEMENT locktoken (href) >
    locktoken uri
  <!ELEMENT lockroot (href) >
    The href element contains the root of the lock.

$Id$
"""
__docformat__ = 'restructuredtext'

import datetime

from zope import component
from zope import interface

import zope.webdav.interfaces
import zope.webdav.properties
from zope.webdav.coreproperties import IActiveLock
from zope.etree.interfaces import IEtree
import zope.webdav.utils

MAXTIMEOUT = (2L ** 32) - 1
DEFAULTTIMEOUT = 12 * 60L


@component.adapter(interface.Interface, zope.webdav.interfaces.IWebDAVMethod)
@interface.implementer(zope.webdav.interfaces.IWebDAVMethod)
def LOCK(context, request):
    """
    If we can adapt the context to a lock manager then we should be able to
    lock the resource.
    """
    lockmanager = zope.webdav.interfaces.IDAVLockmanager(context, None)
    if lockmanager is None:
        return None
    if not lockmanager.islockable():
        return None

    return LOCKMethod(context, request)


class LOCKMethod(object):
    """
    LOCK handler for all objects.
    """
    interface.implements(zope.webdav.interfaces.IWebDAVMethod)
    component.adapts(interface.Interface, zope.webdav.interfaces.IWebDAVRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getDepth(self):
        # default is infinity
        return self.request.getHeader("depth", "infinity")

    def getTimeout(self):
        """
        Return a datetime.timedelta object representing the duration of
        the requested lock token. This information is passed in the `Timeout'
        header and corresponds to the following syntax.

          TimeOut = "Timeout" ":" 1#TimeType
          TimeType = ("Second-" DAVTimeOutVal | "Infinite")
                     ; No LWS allowed within TimeType
          DAVTimeOutVal = 1*DIGIT

        Multiple TimeType entries are listed in order of performace so this
        method will return the first valid TimeType converted to a
        `datetime.timedelta' object or else it returns the default timeout.
        """
        timeout = None
        header = self.request.getHeader("timeout", "infinity")
        for timeoutheader in header.split(","):
            timeoutheader = timeoutheader.strip().lower()

            t = timeoutheader.split("-")
            if len(t) == 2 and t[0].lower().lower() == "second":
                th = t[1]
            elif len(t) == 1 and (t[0] == "infinite" or t[0] == "infinity"):
                th = t[0]
            else:
                raise zope.webdav.interfaces.BadRequest(
                    self.request, message = u"Invalid TIMEOUT header")

            if th == "infinite" or th == "infinite" or th == "infinity":
                timeout = None
            else:
                try:
                    timeout = long(th)
                except ValueError:
                    raise zope.webdav.interfaces.BadRequest(
                        self.request, message = u"Invalid TIMEOUT header")

            if timeout is not None and timeout < MAXTIMEOUT:
                break # we have gotten a valid timeout we want to use.

            timeout = None # try again to find a valid timeout value.

        if timeout is None:
            timeout = DEFAULTTIMEOUT

        return datetime.timedelta(seconds = timeout)

    def LOCK(self):
        # The Lock-Token header is not returned in the response for a
        # successful refresh LOCK request.
        refreshlock = False

        if self.request.xmlDataSource is None:
            errors = self.handleLockRefresh()
            refreshlock = True
        else: # Body => try to lock the resource
            errors = self.handleLock()

        if errors:
            raise zope.webdav.interfaces.WebDAVErrors(self.context, errors)

        etree = component.getUtility(IEtree)

        davprop, adapter = zope.webdav.properties.getProperty(
            self.context, self.request, "{DAV:}lockdiscovery")
        davwidget = zope.webdav.properties.getWidget(
            davprop, adapter, self.request)
        propel = etree.Element(etree.QName("DAV:", "prop"))
        propel.append(davwidget.render())

        activelock = component.getMultiAdapter((self.context, self.request),
                                               IActiveLock)

        self.request.response.setStatus(200)
        self.request.response.setHeader("Content-Type", "application/xml")
        if not refreshlock:
            self.request.response.setHeader("Lock-Token",
                                            "<%s>" % activelock.locktoken[0])

        return etree.tostring(propel)

    def handleLockRefresh(self):
        lockmanager = zope.webdav.interfaces.IDAVLockmanager(self.context)

        if not lockmanager.islocked():
            raise zope.webdav.interfaces.PreconditionFailed(
                self.context, message = u"Context is not locked.")

        locktoken = lockmanager.getActivelock().locktoken[0]
        request_uri = self.request.getHeader("IF", "")
        if not request_uri or \
               request_uri[0] != "<" or request_uri[-1] != ">" or \
               request_uri[1:-1] != locktoken:
            raise zope.webdav.interfaces.PreconditionFailed(
                self.context, message = u"Lock-Token doesn't match request uri")

        timeout = self.getTimeout()
        lockmanager.refreshlock(timeout)

    def handleLock(self):
        errors = []

        xmlsource = self.request.xmlDataSource
        if xmlsource.tag != "{DAV:}lockinfo":
            raise zope.webdav.interfaces.UnprocessableError(
                self.context,
                message = u"LOCK request body must be a `lockinfo' XML element")

        depth = self.getDepth()
        if depth not in ("0", "infinity"):
            raise zope.webdav.interfaces.BadRequest(
                self.request,
                u"Invalid depth header. Must be either '0' or 'infinity'")

        etree = component.getUtility(IEtree)

        timeout = self.getTimeout()

        lockscope = xmlsource.find("{DAV:}lockscope")
        if not lockscope:
            raise zope.webdav.interfaces.UnprocessableError(
                self.context,
                message = u"No `{DAV:}lockscope' XML element in request")
        lockscope_str = zope.webdav.utils.parseEtreeTag(lockscope[0].tag)[1]

        locktype = xmlsource.find("{DAV:}locktype")
        if not locktype:
            raise zope.webdav.interfaces.UnprocessableError(
                self.context,
                message = u"No `{DAV:}locktype' XML element in request")
        locktype_str = zope.webdav.utils.parseEtreeTag(locktype[0].tag)[1]

        owner = xmlsource.find("{DAV:}owner")
        owner_str = etree.tostring(owner)

        lockmanager = zope.webdav.interfaces.IDAVLockmanager(self.context)

        roottoken = None
        try:
            lockmanager.lock(scope = lockscope_str,
                             type = locktype_str,
                             owner = owner_str,
                             duration = timeout,
                             depth = depth)
        except zope.webdav.interfaces.AlreadyLocked, error:
            errors.append(error)

        return errors

################################################################################
#
# UNLOCK method.
#
################################################################################

@component.adapter(interface.Interface, zope.webdav.interfaces.IWebDAVMethod)
@interface.implementer(zope.webdav.interfaces.IWebDAVMethod)
def UNLOCK(context, request):
    """
    If we can adapt the context to a lock manager then we should be able to
    unlock the resource.
    """
    lockmanager = zope.webdav.interfaces.IDAVLockmanager(context, None)
    if lockmanager is None:
        return None
    if not lockmanager.islockable():
        return None

    return UNLOCKMethod(context, request)


class UNLOCKMethod(object):
    """
    UNLOCK handler for all objects.
    """
    interface.implements(zope.webdav.interfaces.IWebDAVMethod)
    component.adapts(interface.Interface, zope.webdav.interfaces.IWebDAVRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def UNLOCK(self):
        locktoken = self.request.getHeader("lock-token", "")
        if len(locktoken) > 1 and locktoken[0] == "<" and locktoken[-1] == ">":
            locktoken = locktoken[1:-1]

        if not locktoken:
            raise zope.webdav.interfaces.BadRequest(
                self.request, message = u"No lock-token header supplied")

        lockmanager = zope.webdav.interfaces.IDAVLockmanager(self.context)
        if not lockmanager.islocked() or \
             lockmanager.getActivelock(self.request).locktoken[0] != locktoken:
            raise zope.webdav.interfaces.ConflictError(
                self.context, message = "object is locked or the lock isn't" \
                                        "in the scope the passed.")

        lockmanager.unlock()

        self.request.response.setStatus(204)
        return ""

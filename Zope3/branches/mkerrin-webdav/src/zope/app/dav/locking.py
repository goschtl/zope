##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Locking support for WebDAV

$Id$
"""
__docformat__ = 'restructuredtext'

import time
import random
from xml.dom import minidom
from xml.parsers import expat

from zope.interface import Interface, implements, implementer
from zope.component import adapter
from zope.publisher.interfaces.http import IHTTPRequest

from zope.app import zapi
from zope.app.form.utility import setUpWidget
from zope.app.locking.interfaces import ILockable, ILockStorage, LockingError
from zope.app.container.interfaces import IReadContainer
from zope.app.http.interfaces import INullResource

from interfaces import IDAVWidget, IActiveLock, ILockEntry, \
     IDAVLockSchema, IIfHeader, IWebDAVRequest
from common import MultiStatus

MAXTIMEOUT = (2L**32)-1
DEFAULTTIMEOUT = 12 * 60L

_randGen = random.Random(time.time())


class DAVLockingError(Exception):
    # override this value
    status = None

    def __init__(self, field_name, error_message):
        self.field_name = field_name
        self.error_message = error_message


class PreConditionFailedError(DAVLockingError):
    """ """
    status = 412


class AlreadyLockedError(DAVLockingError):
    """ """
    status = 423


class DAVConflictError(DAVLockingError):
    """ """
    status = 409


class UnprocessableEntityError(DAVLockingError):
    """ """
    stauts = 422


@adapter(Interface, IWebDAVRequest)
@implementer(Interface)
def LOCKMethodFactory(context, request):
    try:
        lockable = ILockable(context, None)
    except:
        return None
    if lockable is None:
        return None
    return LOCK(context, request)


class LOCK(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

        self._depth = request.getHeader('depth', '0')
        ct = request.getHeader('content-type', 'text/xml')
        if ';' in ct:
            parts = ct.split(';', 1)
            self.content_type = parts[0].strip().lower()
            self.content_type_params = parts[1].strip()
        else:
            self.content_type = ct.lower()
            self.content_type_params = None

        self.default_ns = 'DAV:'
        self.default_ns_prefix = None

        self.errorBody = None

    def generateLockToken(self):
        # is it interesting to provide this has a utility. I don't think so.
        return 'opaquelocktoken:%s-%s-00105A989226:%.03f' % \
               (_randGen.random(), _randGen.random(), time.time())

    def getDepth(self):
        return self._depth

    def getTimeout(self):
        timeoutheader = self.request.getHeader('timeout', 'infinity')

        timeoutheader = timeoutheader.strip().lower()
        t = str(timeoutheader).split('-')[-1]
        if t == 'infinite' or t == 'infinity':
            timeout = DEFAULTTIMEOUT
        else:
            timeout = long(t)

        if timeout > MAXTIMEOUT:
            timeout = DEFAULTTIMEOUT

        return timeout

    def LOCK(self):
        if self.content_type not in ('text/xml', 'application/xml'):
            self.request.response.setStatus(400)
            return ''
        if self.getDepth() not in ('0', 'infinity'):
            self.request.response.setStatus(400)
            return ''

        try:
            xmldoc = minidom.parse(self.request.bodyStream)
        except expat.ExpatError:
            # In this case assume that the bodyStream is empty. We may want to
            # actually test for that case here.
            xmldoc = None

        if xmldoc is None:
            xmldocBody = None
        else:
            xmldocBody = xmldoc.childNodes[0]

        lockable = ILockable(self.context)

        # get lock token from request and pass to handleLockObject
        try:
            if lockable.locked() and xmldoc is None:
                self.handleRefreshLockedObject(self.context)
            else:
                self.handleLockObject(xmldocBody, self.context, None)
        except DAVLockingError, e:
            self.request.response.setStatus(e.status)
            return ''

        if self.errorBody is not None:
            self.request.response.setStatus(207)
            body = self.errorBody.body.toxml('utf-8')
            self.request.response.setResult(body)
            return body

        return self._renderResponse()

    def handleRefreshLockedObject(self, object):
        # request body is empty and the current object is locked.
        lockable = ILockable(object)
        lockinfo = lockable.getLockInfo()

        resource_url = zapi.absoluteURL(object, self.request)
        if IReadContainer.providedBy(object):
            resource_url += '/'

        ifparser = zapi.queryMultiAdapter((object, self.request), IIfHeader)
        if ifparser is not None and not ifparser():
            raise PreConditionFailedError(None, "if header match failed")

        ## the next two lines should be handled in the if parser.
##         if lockinfo.get('lockuri', '') != token:
##             raise PreConditionFailedException, "lock tokens don't match"
        timeout = self.getTimeout()
        lockinfo.timeout = timeout

        if IReadContainer.providedBy(object):
            for id, obj in object.items():
                self.handleRefreshLockedObject(obj)

    def handleLockObject(self, xmldoc, object, token):
        lockable = ILockable(object)
        if lockable.locked():
            raise AlreadyLockedError(None, "object is already locked")

        timeout = self.getTimeout()
        lockinfo = lockable.lock(timeout)
        if not token:
            token = self.generateLockToken()

        lockinfo['lockuri'] = token
        lockinfo['locktoken'] = \
                              '<locktoken><href>%s</href></locktoken>' % token

        adapted = IActiveLock(object)
        for node in xmldoc.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue

            name = node.localName

            field = IActiveLock[name]

            setUpWidget(self, name, field, IDAVWidget, value = None,
                        ignoreStickyValues = False)
            widget = getattr(self, name + '_widget')
            widget.setProperty(node)

            if not widget.hasValidInput():
                raise DAVConflictError(name, "invalid value supplied")

            if not widget.applyChanges(adapted):
                raise UnprocessableEntityError(name, "value failed")

        self.depthRecurse(xmldoc, object, token)

    def _addError(self, object, status):
        if self.errorBody is None:
            self.errorBody = MultiStatus()

        response = self.errorBody.addResponse(object, self.request)
        el = self.errorBody.body.createElementNS(self.default_ns,
                                                 'lockdiscovery')
        response.addPropertyByStatus(self.default_ns, None, el, status)

    def depthRecurse(self, xmldoc, object, token):
        depth = self.getDepth()
        if depth == '0' or not IReadContainer.providedBy(object):
            return

        for id, obj in object.items():
            try:
                self.handleLockObject(xmldoc, obj, token)
            except DAVLockingError, error:
                self._addError(obj, error.status)

    def _renderResponse(self):
        """ Render the response for a successful lock operation """
        lockable = ILockable(self.context)
        assert lockable.locked()
        lockinfo = lockable.getLockInfo()

        ns = self.default_ns
        ns_prefix = self.default_ns_prefix

        resp = minidom.Document()
        prop = resp.createElementNS(ns, 'prop')
        prop.setAttributeNS(ns, 'xmlns', ns)
        resp.appendChild(prop)

        fieldname = 'lockdiscovery'

        adapted = IDAVLockSchema(self.context)

        field = IDAVLockSchema[fieldname]

        setUpWidget(self, fieldname, field, IDAVWidget,
                    value = field.get(adapted),
                    ignoreStickyValues = False)
        widget = getattr(self, fieldname + '_widget', None)
        assert widget is not None
        el = widget.renderProperty()
        prop.appendChild(el)

        body = resp.toxml('utf-8')

        response = self.request.response
        response.setStatus(200)
        response.setHeader('lock-token', '<%s>' % lockinfo['lockuri'])
        response.setHeader('content-type', 'text/xml')
        response.setResult(body)

        return body


@adapter(Interface, IHTTPRequest)
@implementer(Interface)
def UNLOCKMethodFactory(context, request):
    try:
        lockable = ILockable(context, None)
    except:
        return None
    if lockable is None:
        return None
    return UNLOCK(context, request)


class UNLOCK(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def UNLOCK(self):
        lock_token = self.request.getHeader('lock-token', '')
        if lock_token[0] == '<' and lock_token[-1] == '>':
            lock_token = lock_token[1:-1]

        if not lock_token:
            self.request.response.setStatus(412)
            return

        self.handleUnlock(self.context, lock_token)

        self.request.response.setStatus(204)
        return ''

    def handleUnlock(self, object, token):
        lockable = ILockable(object)

        if not lockable.locked():
            # should we raise an unlocked error?? here
            return

        # XXX - this is wrong. We should use an adaption of ILockTracker to
        # find all locks with the lockuri set to token and unlock those tokens
        # has this will fail on a newly created locked item.
        lockinfo = lockable.getLockInfo()
        if lockinfo.get('lockuri', '') != token:
            raise PreConditionFailedError('lockuri',
                                          "lock tokens are not equal")

        lockable.unlock()
        if INullResource.providedBy(object):
            del object.container[object.name]

        # recurise into subfolders if we are a folder.
        if IReadContainer.providedBy(object):
            for id, obj in object.items():
                self.handleUnlock(obj, token)

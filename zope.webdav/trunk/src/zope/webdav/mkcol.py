##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""DAV method MKCOL

$Id$
"""
__docformat__ = 'restructuredtext'

from zope import interface
from zope import component
from zope.filerepresentation.interfaces import IWriteDirectory
from zope.filerepresentation.interfaces import IDirectoryFactory
import zope.event
from zope.lifecycleevent import ObjectCreatedEvent
import zope.app.http.interfaces

import zope.webdav.interfaces

class NullResource(object):
    """MKCOL handler for creating collections"""

    # MKCOL is only supported on unmapped urls.
    interface.implements(zope.webdav.interfaces.IWebDAVMethod)
    component.adapts(zope.app.http.interfaces.INullResource,
                     zope.webdav.interfaces.IWebDAVRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def MKCOL(self):
        request = self.request
        data = request.bodyStream.read()
        if len(data):
            # We don't (yet) support a request body on MKCOL.
            raise zope.webdav.interfaces.UnsupportedMediaType(
                self.context,
                message = u"A request body is not supported for a MKCOL method")

        container = self.context.container
        name = self.context.name

        dir = IWriteDirectory(container, None)
        if dir is None:
            raise zope.webdav.interfaces.ForbiddenError(
                self.context, message = u"")

        factory = IDirectoryFactory(container)
        newdir = factory(name)
        zope.event.notify(ObjectCreatedEvent(newdir))
        dir[name] = newdir

        request.response.setStatus(201)
        return ""

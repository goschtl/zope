##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""DAV method MKCOL

$Id: mkcol.py,v 1.1 2003/06/23 17:21:08 sidnei Exp $
"""
__metaclass__ = type

from zope.app.interfaces.file import IWriteDirectory
from zope.app.interfaces.file import IDirectoryFactory
from zope.app.interfaces.container import IZopeWriteContainer
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.component import queryAdapter, getAdapter

class NullResource:
    """MKCOL handler for creating collections
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def MKCOL(self):
        request = self.request
        data = request.bodyFile
        data.seek(0)
        data = data.read()
        if len(data):
            # We don't (yet) support a request body on MKCOL.
            request.response.setStatus(415)
            return ''

        container = self.context.container
        name = self.context.name

        dir = queryAdapter(container, IWriteDirectory, None)
        if dir is None:
            request.response.setStatus(403)
            return ''

        dir = getAdapter(dir, IZopeWriteContainer)

        factory = getAdapter(container, IDirectoryFactory)
        newdir = factory(name)
        publish(self.context, ObjectCreatedEvent(newdir))
        dir.setObject(name, newdir)

        request.response.setStatus(201)
        return ''

class MKCOL:
    """MKCOL handler for existing objects
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def MKCOL(self):
        # 405 (Method Not Allowed) - MKCOL can only be executed on a
        # deleted/non-existent resource.
        self.request.response.setStatus(405)
        return ''

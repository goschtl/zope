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

$Id: mkcol.py,v 1.5 2004/03/06 17:48:48 jim Exp $
"""
from zope.app import zapi
from zope.app.interfaces.file import IWriteDirectory
from zope.app.interfaces.file import IDirectoryFactory
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent

class NullResource(object):
    """MKCOL handler for creating collections"""

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

        dir = IWriteDirectory(container, None)
        if dir is None:
            request.response.setStatus(403)
            return ''

        factory = IDirectoryFactory(container)
        newdir = factory(name)
        publish(self.context, ObjectCreatedEvent(newdir))
        dir[name] = newdir

        request.response.setStatus(201)
        return ''


class MKCOL(object):
    """MKCOL handler for existing objects"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def MKCOL(self):
        # 405 (Method Not Allowed) - MKCOL can only be executed on a
        # deleted/non-existent resource.
        self.request.response.setStatus(405)
        return ''

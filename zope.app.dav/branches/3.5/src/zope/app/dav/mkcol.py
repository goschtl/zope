##############################################################################
# Copyright (c) 2003 Zope Foundation and Contributors.
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

from zope.filerepresentation.interfaces import IWriteDirectory
from zope.filerepresentation.interfaces import IDirectoryFactory
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

class NullResource(object):
    """MKCOL handler for creating collections"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def MKCOL(self):
        request = self.request
        data = request.bodyStream.read()
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
        notify(ObjectCreatedEvent(newdir))
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

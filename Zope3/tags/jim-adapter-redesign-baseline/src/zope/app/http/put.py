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
"""HTTP `PUT` verb

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.component import queryAdapter
from zope.app.http.interfaces import INullResource
from zope.app.filerepresentation.interfaces import IWriteFile
from zope.app.filerepresentation.interfaces import IWriteDirectory, IFileFactory
from zope.event import notify
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.interface import implements

class NullResource(object):
    """Object representing objects to be created by a `PUT`.
    """

    implements(INullResource)

    def __init__(self, container, name):
        self.container = container
        self.name = name


class NullPUT(object):
    """Put handler for null resources (new file-like things)

    This view creates new objects in containers.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def PUT(self):
        request = self.request

        for name in request:
            if name.startswith('HTTP_CONTENT_'):
                # Unimplemented content header
                request.response.setStatus(501)
                return ''

        body = request.bodyFile
        name = self.context.name
        container = self.context.container

        # Find the extension
        ext_start = name.rfind('.')
        if ext_start > 0:
            ext = name[ext_start:]
        else:
            ext = "."

        # Get a "directory" surrogate for the container
        dir = IWriteDirectory(container, None)

        # Now try to get a custom factory for he container
        factory = queryAdapter(container, IFileFactory, ext)

        # Fall back to a non-custom one
        if factory is None:
            factory = IFileFactory(container)

        # TODO: Need to add support for large files
        data = body.read()

        newfile = factory(name, request.getHeader('content-type', ''), data)
        notify(ObjectCreatedEvent(newfile))

        dir[name] = newfile

        request.response.setStatus(201)
        return ''

class FilePUT(object):
    """Put handler for existing file-like things
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def PUT(self):
        request = self.request

        for name in request:
            if name.startswith('HTTP_CONTENT_'):
                # Unimplemented content header
                request.response.setStatus(501)
                return ''

        body = self.request.bodyFile
        file = self.context
        adapter = IWriteFile(file)

        # TODO: Need to add support for large files
        data = body.read()

        adapter.write(data)

        return ''



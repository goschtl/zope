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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: put.py,v 1.1 2003/02/07 15:59:37 jim Exp $
"""
__metaclass__ = type

from zope.component import getAdapter, queryAdapter
from zope.app.interfaces.http import INullResource
from zope.app.interfaces.file import IWriteFile, IWriteDirectory, IFileFactory
from zope.app.interfaces.container import IZopeWriteContainer
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
        
class NullResource:
    """Object representing objects to be created by a PUT.
    """

    __implements__ = INullResource

    def __init__(self, container, name):
        self.container = container
        self.name = name


class NullPUT:
    """Put handler for null resources (new file-like things)

    This view creates new objects in containers.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def PUT(self):
        body = self.request.bodyFile
        name = self.context.name
        container = self.context.container

        # Find the extension
        ext_start = name.rfind('.')
        if ext_start > 0:
            ext = name[ext_start:]
        else:
            ext = "."

        # Get a "directory" surrogate for the container
        dir = queryAdapter(container, IWriteDirectory)

        # Get the zope adapter for that
        dir = getAdapter(dir, IZopeWriteContainer)

        # Now try to get a custom factory for he container
        factory = queryAdapter(container, IFileFactory, name=ext)

        # Fall back to a non-custom one
        if factory is None:
            factory = getAdapter(container, IFileFactory)

        # XXX Need to add support for large files
        data = body.read()

        newfile = factory(name,
                          self.request.getHeader('content-type', ''),
                          data)
        publish(self.context, ObjectCreatedEvent(newfile))
        dir.setObject(name, newfile)
        
        return ''

class FilePUT:
    """Put handler for existing file-like things
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def PUT(self):
        body = self.request.bodyFile
        file = self.context
        adapter = getAdapter(file, IWriteFile)

        # XXX Need to add support for large files
        data = body.read()

        adapter.write(data)

        return ''

        

##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Filesystem synchronization support.

$Id: fssync.py,v 1.12 2003/09/21 17:31:52 jim Exp $
"""

from zope.app.fssync.classes import ObjectEntryAdapter, AttrMapping
from zope.app.interfaces.fssync import IObjectFile, IContentDirectory
from zope.interface import implements

class FileAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for file objects."""

    implements(IObjectFile)

    def getBody(self):
        return self.context.getData()

    def setBody(self, data):
        self.context.setData(data)

    def extra(self):
        return AttrMapping(self.context, ('contentType',))

class DirectoryAdapter(ObjectEntryAdapter):
    """Folder adapter to provide a file-system representation."""

    implements(IContentDirectory)

    def contents(self):
        result = []
        for name, object in self.context.items():
            result.append((name, object))
        return result

class ZPTPageAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for ZPT page objects."""

    implements(IObjectFile)

    def getBody(self):
        return self.context.getSource()

    def setBody(self, data):
        # Convert the data to Unicode, since that's what ZPTPage wants;
        # it's normally read from a file so it'll be bytes.
        # XXX This will die if it's not ASCII.  Guess encoding???
        self.context.setSource(unicode(data))

class DTMLPageAdapter(ObjectEntryAdapter):

    implements(IObjectFile)

    def getBody(self):
        return self.context.getSource()

    def setBody(self, data):
        self.context.setSource(data)

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

$Id: fssync.py,v 1.9 2003/06/01 15:59:30 jim Exp $
"""

from zope.app.content.file import File
from zope.app.content.folder import Folder
from zope.app.content.zpt import ZPTPage
from zope.app.fssync.classes import ObjectEntryAdapter, AttrMapping
from zope.app.interfaces.fssync import IObjectFile, IContentDirectory
from zope.app.context import ContextWrapper

class FileAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for file objects."""

    __implements__ =  IObjectFile

    def getBody(self):
        return self.context.getData()

    def setBody(self, data):
        self.context.setData(data)

    def extra(self):
        return AttrMapping(self.context, ('contentType',))

class DirectoryAdapter(ObjectEntryAdapter):
    """Folder adapter to provide a file-system representation."""

    __implements__ =  IContentDirectory

    def contents(self):
        result = []
        for name, object in self.context.items():
            object = ContextWrapper(object, self.context, name=name)
            result.append((name, object))
        return result

class ZPTPageAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for ZPT page objects."""

    __implements__ =  IObjectFile

    def getBody(self):
        return self.context.getSource()

    def setBody(self, data):
        # Convert the data to Unicode, since that's what ZPTPage wants;
        # it's normally read from a file so it'll be bytes.
        # XXX This will die if it's not ASCII.  Guess encoding???
        self.context.setSource(unicode(data))

class DTMLPageAdapter(ObjectEntryAdapter):

    __implements__ = IObjectFile

    def getBody(self):
        return self.context.getSource()

    def setBody(self, data):
        self.context.setSource(data)

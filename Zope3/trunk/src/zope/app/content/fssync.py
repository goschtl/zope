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

$Id: fssync.py,v 1.2 2003/05/05 18:01:00 gvanrossum Exp $
"""

from zope.app.interfaces.fssync import IObjectFile, IContentDirectory
from zope.app.fssync.classes import ObjectEntryAdapter, AttrMapping
from zope.proxy.context import ContextWrapper

_attrs = ('contentType', )

class ObjectFileAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for file objects."""

    __implements__ =  IObjectFile

    def getBody(self):
        "See IObjectFile"
        return self.context.getData()

    def setBody(self, data):
        "See IObjectFile"
        self.context.setData(data)

    def extra(self):
        "See IObjectEntry"
        return AttrMapping(self.context, _attrs)

class ObjectDirectory(ObjectEntryAdapter):
    """Folder adapter to provide a file-system representation."""

    __implements__ =  IContentDirectory

    def contents(self):
        "See IObjectDirectory"
        result = []
        for name, object in self.context.items():
            object = ContextWrapper(object, self.context, name=name)
            result.append((name, object))
        return result

class ZPTObjectFileAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for ZPT page objects."""

    __implements__ =  IObjectFile

    def getBody(self):
        "See IObjectFile"
        return self.context.getSource()

    def setBody(self, data):
        "See IObjectFile"
        self.context.setSource(data)

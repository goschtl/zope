##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""WebDAV-related Adapters

$Id$
"""
from xml.dom import minidom

from zope.interface import implements

from zope.app import zapi
from zope.app.dav.interfaces import IDAVSchema
from zope.app.dublincore.interfaces import IDCTimes
from zope.app.filerepresentation.interfaces import IReadDirectory
from zope.app.size.interfaces import ISized

class DAVSchemaAdapter:
    """An adapter for all content objects that provides the basic DAV
    schema/namespace."""
    implements(IDAVSchema)

    def __init__(self, object):
        self.context = object

    def displayname(self):
        value = zapi.name(self.context)
        if IReadDirectory(self.context, None) is not None:
            value = value + '/'
        return value

    def creationdate(self):
        value = IDCTimes(self.context).created
        if value is None:
            return ''
        value = value.strftime('%Y-%m-%d %TZ')
        return value

    def resourcetype(self):
        value = IReadDirectory(self.context, None)
        xml = minidom.Document()
        if value is not None:
            node = xml.createElement('collection')
            return node
        return ''

    def getcontentlength(self):
        value = ISized(self.context).sizeForDisplay()
        return str(value)

    def getlastmodified(self):
        value = IDCTimes(self.context).modified
        if value is None:
            return ''
        value = value.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return value

    def executable(self):
        return ''

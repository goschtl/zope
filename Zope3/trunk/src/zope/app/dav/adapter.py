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
"""WebDAV Adapters

$Id: adapter.py,v 1.6 2004/03/03 11:03:59 philikon Exp $
"""

from xml.dom import minidom
from zope.component import getAdapter, queryAdapter
from zope.app.dublincore.interfaces import IDCTimes
from zope.app.interfaces.file import IReadDirectory
from zope.app.size.interfaces import ISized
from zope.app import zapi

class DAVSchemaAdapter:

    def __init__(self, object):
        self.context = object

    def displayname(self):
        value = zapi.name(self.context)
        if queryAdapter(self.context, IReadDirectory, None) is not None:
            value = value + '/'
        return value

    def creationdate(self):
        value = getAdapter(self.context, IDCTimes).created
        if value is None:
            return ''
        value = value.strftime('%Y-%m-%d %TZ')
        return value

    def resourcetype(self):
        value = queryAdapter(self.context, IReadDirectory, None)
        xml = minidom.Document()
        if value is not None:
            node = xml.createElement('collection')
            return node
        return ''

    def getcontentlength(self):
        value = getAdapter(self.context, ISized).sizeForDisplay()
        return str(value)

    def getlastmodified(self):
        value = getAdapter(self.context, IDCTimes).modified
        if value is None:
            return ''
        value = value.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return value

    def executable(self):
        return ''

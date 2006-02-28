##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""FSSync adapters for local presentation components

$Id$
"""
__docformat__ = "reStructuredText"
from zope.interface import implements

from zope.fssync.server.entryadapter import ObjectEntryAdapter, AttrMapping
from zope.fssync.server.interfaces import IObjectDirectory, IObjectFile


class PageFolderAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for `PageFolder` objects."""
    implements(IObjectDirectory)

    _attrNames = ('factoryName', 'required', 'permission')

    def contents(self):
        return self.context.items()

    def extra(self):
        return AttrMapping(self.context, self._attrNames)


class ZPTPageAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for `ZPTTemplate` objects."""

    implements(IObjectFile)

    def getBody(self):
        return self.context.source

    def setBody(self, data):
        # Convert the data to Unicode, since that's what ZPTTemplate
        # wants; it's normally read from a file so it'll be bytes.
        # The default encoding in Zope is UTF-8.
        self.context.source = data.decode('UTF-8')

    def extra(self):
        return AttrMapping(self.context, ('contentType', 'expand'))

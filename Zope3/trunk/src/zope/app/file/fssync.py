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

$Id: fssync.py,v 1.2 2004/02/24 16:49:48 philikon Exp $
"""
from zope.interface import implements
from zope.fssync.server.entryadapter import ObjectEntryAdapter
from zope.fssync.server.interfaces import IObjectFile

class FileAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for file objects.
    """
    implements(IObjectFile)

    def getBody(self):
        return self.context.getData()

    def setBody(self, data):
        self.context.setData(data)

    def extra(self):
        return AttrMapping(self.context, ('contentType',))

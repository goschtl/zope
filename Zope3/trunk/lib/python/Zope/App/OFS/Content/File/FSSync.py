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
"""
$Id: FSSync.py,v 1.2 2002/10/11 06:28:06 jim Exp $
"""

__metaclass__ = type


from Zope.App.FSSync.IObjectFile import IObjectFile
from Zope.App.FSSync.ObjectEntryAdapter import ObjectEntryAdapter
from Zope.App.FSSync.AttrMapping import AttrMapping

attrs = ('contentType', )

class ObjectFileAdapter(ObjectEntryAdapter):
    "ObjectFile adapter for file objects"

    __implements__ =  IObjectFile

    def getBody(self):
        "See Zope.App.FSSync.IObjectFile.IObjectFile"
        return self.context.getData() or ''

    def setBody(self, data):
        "See Zope.App.FSSync.IObjectFile.IObjectFile"
        self.context.setData(data)

    def extra(self):
        "See Zope.App.FSSync.IObjectEntry.IObjectEntry"
        return AttrMapping(self.context, attrs)

__doc__ = ObjectFileAdapter.__doc__ + __doc__

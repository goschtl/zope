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
from Zope.App.Security import Settings

class ObjectFileAdapter(ObjectEntryAdapter):
    "ObjectFile adapter for file objects"

    __implements__ =  IObjectFile

    def getBody(self):
        "See Zope.App.FSSync.IObjectFile.IObjectFile"

        r = []

        for row, col, setting in self.context.getAllCells():
            r.append('%s\t%s\t%s\n' % 
                     (setting.getName(),
                      row,
                      col)
                     )

        return ''.join(r)

    def setBody(self, body):
        "See Zope.App.FSSync.IObjectFile.IObjectFile"

        context = self.context

        for row, col, setting in context.getAllCells():
            context.delCell(row, col)
        
        for record in body.split('\n'):
            record = record.strip()
            if record:
                setting, row, col = record.split()
                context.addCell(row, col, getattr(Settings, setting))

            

__doc__ = ObjectFileAdapter.__doc__ + __doc__

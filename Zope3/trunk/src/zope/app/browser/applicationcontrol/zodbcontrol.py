##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
""" Server Control View

$Id: zodbcontrol.py,v 1.1 2003/07/31 21:37:27 srichter Exp $
"""
from zodb.storage.file.errors import FileStorageError
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.applicationcontrol import IZODBControl
from zope.component import getAdapter


class ZODBControlView:

     def getDatabaseSize(self):
         zodbcontrol = getAdapter(self.context, IZODBControl)
         size = zodbcontrol.getDatabaseSize(
                    self.request.publication.db)
         if size > 1024**2:
             return "%.1f MB" %(float(size)/1024**2)
         elif size > 1024:
             return "%.1f kB" %(float(size)/1024)
         else:
             return "%i Bytes" %size

     def pack(self):
         """Do the packing!"""
         status = ''

         if 'PACK' in self.request:
              zodbcontrol = getAdapter(self.context, IZODBControl)
              try:
                   zodbcontrol.pack(self.request.publication.db,
                                    int(self.request.get('days', 0)))
                   status = _('ZODB successfully packed.')
              except FileStorageError, err:
                   status = _(err)

         return status

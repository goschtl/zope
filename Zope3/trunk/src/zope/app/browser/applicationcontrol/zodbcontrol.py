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

$Id: zodbcontrol.py,v 1.4 2004/02/20 16:57:19 fdrake Exp $
"""
from ZODB.FileStorage.FileStorage import FileStorageError
from zope.app.interfaces.applicationcontrol import IZODBControl
from zope.component import getAdapter

from zope.app.i18n import ZopeMessageIDFactory as _

class ZODBControlView:

    def getDatabaseSize(self):
        """Get the database size in a human readable format."""
        zodbcontrol = getAdapter(self.context, IZODBControl)
        size = zodbcontrol.getDatabaseSize(self.request.publication.db)
        if size > 1024**2:
            size_str = _("${size} MB")
            size_str.mapping = {'size': "%.1f" %(float(size)/1024**2)}
        elif size > 1024:
            size_str = _("${size} kB")
            size_str.mapping = {'size': "%.1f" %(float(size)/1024)}
        else:
            size_str = _("${size} Bytes")
            size_str.mapping = {'size': "%i" %size}

        return size_str
        

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

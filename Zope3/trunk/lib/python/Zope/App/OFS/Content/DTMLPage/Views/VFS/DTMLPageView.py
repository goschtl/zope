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
"""VFS-View for IDTMLPage

VFS-view implementation for a DTML Page. 

$Id: DTMLPageView.py,v 1.1 2002/12/20 10:31:46 srichter Exp $
"""
from Zope.Publisher.VFS.VFSFileView import VFSFileView

class DTMLPageView(VFSFileView):

    def _setData(self, data):
        self.context.setSource(data)

    def _getData(self):
        return self.context.getSource()

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

$Id: dtmlpageview.py,v 1.2 2002/12/25 14:13:29 jim Exp $
"""
from zope.publisher.vfs import VFSFileView

class DTMLPageView(VFSFileView):

    def _setData(self, data):
        self.context.setSource(data)

    def _getData(self):
        return self.context.getSource()

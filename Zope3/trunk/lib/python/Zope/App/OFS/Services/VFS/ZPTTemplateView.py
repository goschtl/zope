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
"""VFS-View for IZPTTemplate

VFS-view implementation for a ZPT Template. 

$Id: ZPTTemplateView.py,v 1.1 2002/12/23 08:15:39 srichter Exp $
"""
from Zope.Publisher.VFS.VFSFileView import VFSFileView

class ZPTTemplateView(VFSFileView):

    def _setData(self, data):
        self.context.source = data

    def _getData(self):
        return self.context.source

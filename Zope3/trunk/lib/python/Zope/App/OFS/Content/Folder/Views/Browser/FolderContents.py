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
"""
    Define view component for folder contents.

$Id: FolderContents.py,v 1.4 2002/10/02 18:51:46 jim Exp $
"""

import os

from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.App.OFS.Container.Views.Browser.Contents import Contents

class FolderContents(Contents):

    def addServiceManager(self, REQUEST=None):
        """Create a service manager then add it to the folder."""

        sm = ServiceManager()
        if self.context.hasServiceManager():
            raise 'HasServiceManager', (
                  'This folder already contains a service manager')
        self.context.setServiceManager(sm)
        if REQUEST is not None:
            return self.contents()

    contents = ViewPageTemplateFile('contents.pt')

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

Revision information: $Id: pagefolder.py,v 1.1 2003/03/23 16:45:43 jim Exp $
"""
from zope.app.browser.container.contents import Contents
from zope.app.interfaces.services.pagefolder import IPageFolder
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.services.zpt import ZPTTemplate

class PageFolderContents(Contents):

    __used_for__ = IPageFolder

    index = ViewPageTemplateFile('pagefolder_contents.pt')

    def add(self, name):
        self.context.setObject(name, ZPTTemplate())
        self.request.response.redirect('@@contents.html')

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

$Id: pagefolder.py,v 1.3 2003/08/07 17:41:03 srichter Exp $
"""
from zope.app.interfaces.services.pagefolder import IPageFolder

class PageFolderDefaultConfiguration:

    def changed(self):
        """Apply changes to existing configurations"""
        __used_for__ = IPageFolder

        folder = self.context
        if folder.apply:
            folder.applyDefaults()

            

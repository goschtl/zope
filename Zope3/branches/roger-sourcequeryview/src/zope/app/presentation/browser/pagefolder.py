##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Page Folder Default Configuration View.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.presentation.pagefolder import IPageFolder

class PageFolderDefaultConfiguration(object):

    def changed(self):
        """Apply changes to existing configurations"""
        __used_for__ = IPageFolder

        folder = self.context
        if folder.apply:
            folder.applyDefaults()

            

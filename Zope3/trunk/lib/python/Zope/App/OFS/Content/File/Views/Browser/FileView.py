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

$Id: FileView.py,v 1.2 2002/06/10 23:27:58 jim Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView


class FileView(BrowserView):

    def __call__(self):
        """Call the File"""
        request = self.request
        if request is not None:
            request.getResponse().setHeader('Content-Type',
                                       self.context.getContentType())
            request.getResponse().setHeader('Content-Length',
                                       self.context.getSize())

        return self.context.getData()

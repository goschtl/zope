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
"""File views.

$Id: file.py,v 1.4 2003/08/06 14:41:41 srichter Exp $
"""
from zope.app.browser.form.widget import FileWidget
from zope.app.form.widget import CustomWidget

__metaclass__ = type

class FileView:

    def show(self):
        """Call the File"""
        request = self.request
        if request is not None:
            request.response.setHeader('Content-Type',
                                       self.context.getContentType())
            request.response.setHeader('Content-Length',
                                       self.context.getSize())

        return self.context.getData()


class FileUpload:
    """File editing mix-in that uses a file-upload widget."""

    data_widget = CustomWidget(FileWidget)

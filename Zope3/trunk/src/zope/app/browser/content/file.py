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

$Id: file.py,v 1.2 2002/12/25 14:12:30 jim Exp $
"""

from zope.publisher.browser import BrowserView


class FileView(BrowserView):

    def show(self):
        """Call the File"""
        request = self.request
        if request is not None:
            request.response.setHeader('Content-Type',
                                       self.context.getContentType())
            request.response.setHeader('Content-Length',
                                       self.context.getSize())

        return self.context.getData()


"""
$Id: file.py,v 1.2 2002/12/25 14:12:30 jim Exp $
"""

__metaclass__ = type

from zope.app.browser.form.widget import FileWidget
from zope.app.form.widget import CustomWidget

class FileUpload:
    """File editing mix-in that uses a file-upload widget.
    """

    data = CustomWidget(FileWidget)



__doc__ = FileUpload.__doc__ + __doc__

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
"""Define view component for image editing.

$Id: ImageUpload.py,v 1.3 2002/12/03 14:01:42 runyaga Exp $
"""
from Zope.App.OFS.Content.File.Views.Browser.FileUpload import FileUpload
from Zope.Event import publish
from Zope.Event.ObjectEvent import ObjectModifiedEvent

class ImageUpload(FileUpload):
    """Image edit view mix-in that provides access to image size info"""

    def size(self):
        sx, sy = self.context.getImageSize()
        return "%s x %s pixels" % (sx > 0 and sx or 0, sx > 0 and sy or 0)
            

    def apply_update(self, data):
        """Apply user inputs

        These inputs have already been validated.

        Return a boolean indicating whether we changed anything,
        """

        unchanged = True

        # if we can compute the content type from the raw data, then
        # that overrides what the user provided, so set the content
        # type first.

        contentType = data.get('contentType')
        if contentType and contentType != self.context.contentType:
            self.context.contentType = contentType
            unchanged = False

        if 'data' in data:
            self.context.data = data['data']
            unchanged = False
        
        if not unchanged:
            publish(self.context, ObjectModifiedEvent(self.context))

        return unchanged

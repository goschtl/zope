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
Define view component for image editing.

Revision Information:
$Id: ImageEdit.py,v 1.2 2002/06/10 23:28:04 jim Exp $
"""

from Zope.App.Formulator.Form import Form
from Zope.App.PageTemplate import ViewPageTemplateFile


class ImageEdit(Form):

    __implements__ = Form.__implements__

    name = 'editForm'     
    title = 'Edit Form'
    description = ('This edit form allows you to make changes to the ' +
                   'properties of this image.')

    _fieldViewNames = ['ContentTypeFieldView', 'DataFieldView']
    template = ViewPageTemplateFile('edit.pt')
    
    def getImageSize(self):
        size=self.context.getImageSize()
        return "%d x %d" % (size[0], size[1])
 

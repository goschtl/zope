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

$Id: ImageEdit.py,v 1.3 2002/07/19 13:12:32 srichter Exp $
"""
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.App.Forms.Views.Browser import Widget 
from Zope.App.Forms.Views.Browser.FormView import FormView

class ImageEdit(FormView):
    form = ViewPageTemplateFile('edit.pt')
    custom_widgets = {'data': Widget.FileWidget}
    fields_order = ('contentType', 'data')
 

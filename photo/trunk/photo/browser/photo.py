##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Browser View for the Photo class

$Id: photo.py,v 1.3 2004/03/18 18:04:55 philikon Exp $
"""
from zope.app.file.browser.image import ImageData
from zope.app.form.browser import FileWidget, ChoiceDisplayWidget
from zope.app.form import CustomWidgetFactory

# from photo import Photo

class PhotoData(ImageData):

    def __call__(self):
        if 'display' in self.request:
            dispId = self.request['display']
        else:
            dispId = None
        image = self.context.getImage(dispId)
        if image is not None: 
            if self.request is not None:
                self.request.response.setHeader('content-type',
                                                image.contentType)
                return image.data
        else:
            return ''

    def tag(self, height=None, width=None, alt=None,
            scale=0, xscale=0, yscale=0, css_class=None, **args):
        if width is None:
            width = self.context.getImage().getImageSize()[0]
        if height is None:
            height = self.context.getImage().getImageSize()[1]
        return super(PhotoData, self).tag(height, width, alt, scale,
                                          xscale, yscale, css_class, **args)

## These classes are no longer used (i.e. referenced from zcml)
class CurrentDisplayIdFix:
    """Changes the currentIdDisplay widget to be a ListWidget.

    This way we don't get the values sorted and can specify a
    text which represents each value.
    """
    ## changed ListWidget to ListDisplayWidget -- don't know the best option
    currentDisplayId_widget = CustomWidgetFactory(ChoiceDisplayWidget, size=1)

class PhotoAdd(CurrentDisplayIdFix):
    """Class to change some of the widgets om the add page for
    the Photo class.
    """
    data_widget = CustomWidgetFactory(FileWidget)

class PhotoEdit(CurrentDisplayIdFix):
    """Class to change som of the widgets on the edit page for
    the Photo class.
    """
    data_widget = CustomWidgetFactory(FileWidget)

class PhotoUpload(PhotoEdit):
    """The same as PhotoEdit but we can now upload a file as well"""
    data_widget = CustomWidgetFactory(FileWidget)

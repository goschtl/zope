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
"""Define view component for image editing.

$Id$
"""
__docformat__ = 'restructuredtext'

from urllib import quote

from zope.i18n.negotiator import negotiator

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.file.browser.image import ImageData
from zope.app.size import byteDisplay

class I18nImageEdit(object):

    name = 'editForm'
    title = _('Edit Form')
    description = _('This edit form allows you to make changes to the ' +
                   'properties of this image.')

    def size(self, language=None):
        sized = ISized(self.context._get(language))
        return sized.sizeForDisplay()

    def action(self, contentType, data, language, defaultLanguage,
               selectLanguage=None, removeLanguage=None,
               addLanguage=None, newLanguage=None):
        if selectLanguage:
            pass
        elif removeLanguage:
            self.context.removeLanguage(language)
            language = self.context.getDefaultLanguage()
        else:
            if addLanguage:
                language = newLanguage
            self.context.setDefaultLanguage(defaultLanguage)
            self.context.setData(data, language)
            self.context.contentType = contentType
        return self.request.response.redirect(self.request.URL[-1] +
                      "/upload.html?language=%s" % quote(language, ''))

    
class I18nImageData(ImageData):

    def __call__(self):
        image = self.context
        language = None
        if self.request is not None:
            langs = self.context.getAvailableLanguages()
            language = negotiator.getLanguage(langs, self.request)
            self.request.response.setHeader('content-type', image.contentType)
        return image.getData(language)


    def tag(self, height=None, width=None, **args):
        """See `ImageData.tag.`"""

        language = None
        if self.request is not None and \
           (width is None or height is None):
            langs = self.context.getAvailableLanguages()
            language = negotiator.getLanguage(langs, self.request)

        if width is None:
            width = self.context.getImageSize(language)[0]
        if height is None:
            height = self.context.getImageSize(language)[1]
        return ImageData.tag(self, width=width, height=height, **args)

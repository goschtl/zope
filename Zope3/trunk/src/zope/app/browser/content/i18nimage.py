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
$Id: i18nimage.py,v 1.2 2002/12/25 14:12:30 jim Exp $
"""

from zope.app.browser.content.image import ImageData
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.i18n.negotiator import negotiator
from zope.publisher.browser import BrowserView


class I18nImageEdit(BrowserView):

    __implements__ = BrowserView.__implements__

    name = 'editForm'
    title = 'Edit Form'
    description = ('This edit form allows you to make changes to the ' +
                   'properties of this image.')

    def getImageSize(self, language=None):
        size = self.context.getImageSize(language)
        return "%d x %d" % (size[0], size[1])

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
            self.context.edit(data, contentType, language)
        return self.request.response.redirect(self.request.URL[-1] +
                      "/editForm.html?language=%s" % language)  # XXX url_quote


class I18nImageData(ImageData):

    def __call__(self):
        image = self.context
        language = None
        if self.request is not None:
            langs = self.context.getAvailableLanguages()
            language = negotiator.getLanguage(langs, self.request)

            self.request.response.setHeader('content-type',
                                                 image.getContentType())
            # XXX: no content-length?  See ImageData.__call__
        return image.getData(language)


    def tag(self, height=None, width=None, **args):
        """See ImageData.tag."""

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

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
""" Define view component for internationalized images.

$Id: I18nImageData.py,v 1.1 2002/06/25 10:54:24 mgedmin Exp $
"""

from ImageData import ImageData
from Zope.I18n.Negotiator import negotiator

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

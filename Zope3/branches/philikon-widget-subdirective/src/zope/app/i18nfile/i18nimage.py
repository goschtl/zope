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
"""I18n-aware Image Content Component

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.app.file.image import Image, getImageInfo
from zope.app.i18nfile.i18nfile import I18nFile

from interfaces import II18nImage


class I18nImage(I18nFile):
    """An internationalized Image object.  Note that images of all
    languages share the same content type.
    """

    implements(II18nImage)

    def _create(self, data):
        return Image(data)

    def setData(self, data, language=None):
        '''See interface `II18nFile`'''
        super(I18nImage, self).setData(data, language)

        if language is None or language == self.getDefaultLanguage():
            # Uploading for the default language only overrides content
            # type.  Note: do not use the argument data here, it doesn't
            # work.
            contentType = getImageInfo(self.getData(language))[0]
            if contentType:
                self.contentType = contentType

    def getImageSize(self, language=None):
        '''See interface `II18nImage`'''
        return self.getObject(language).getImageSize()

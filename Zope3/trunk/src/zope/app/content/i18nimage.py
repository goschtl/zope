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
"""Internationalized Image Content Component.

$Id: i18nimage.py,v 1.5 2004/02/14 03:27:14 srichter Exp $
"""
from zope.app.content.image import Image, getImageInfo
from zope.app.content.i18nfile import I18nFile
from zope.app.interfaces.content.i18n import II18nImage
from zope.interface import implements

class I18nImage(I18nFile):
    """An internationalized Image object.

    Note that images of all languages share the same content type.
    """
    implements(II18nImage)

    def _create(self, data):
        return Image(data)

    def setData(self, data, language=None):
        '''See zope.app.interfaces.file.IFile'''
        super(I18nImage, self).setData(data, language)

        if language is None or language == self.getDefaultLanguage():
            # Uploading for the default language only overrides content
            # type.  Note: do not use the argument data here, it doesn't
            # work.
            contentType = getImageInfo(self.getData(language))[0]
            if contentType:
                self.setContentType(contentType)

    def getImageSize(self, language=None):
        '''See zope.app.interfaces.image.IImage'''
        return self._get(language).getImageSize()

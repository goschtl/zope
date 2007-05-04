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
"""I18n-aware file and image interfaces.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.i18n.interfaces import II18nAware
from zope.app.file.interfaces import IFile, IImage

class II18nFile(IFile, II18nAware):
    """I18n aware file interface."""

    def getObject(language=None):
        """Return a subobject for a given language,
        and if it does not exist, return a subobject for the default
        language.
        """

    def getData(language=None):
        """Return the object data for a given language
        or for the default language.
        """

    def setData(data, language=None):
        """Set the object data for a given language
        or for the default language.
        """

    def getSize(language=None):
        """Return the byte-size of the data of the object for a given language
        or for the default language.
        """

    def removeLanguage(language):
        """Remove translated content for a given language.
        """

class II18nImage(II18nFile, IImage):
    """I18n aware image interface."""

    def getImageSize(language=None):
        """Return a tuple (x, y) that describes the dimensions of the object
        for a given language or for the default language.
        """

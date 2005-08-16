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
"""I18n-aware image interfaces.

$Id: interfaces.py 26890 2004-08-04 04:17:33Z pruggera $
"""
__docformat__ = 'restructuredtext'

from zope.i18n.interfaces import II18nAware
from zope.app.i18nfile.interfaces import II18nFile
from zope.app.image.interfaces import IImage


class II18nImage(II18nFile, IImage):
    """I18n aware image interface."""

    def getImageSize(language=None):
        """Return a tuple (x, y) that describes the dimensions of the object
        for a given language or for the default language.
        """

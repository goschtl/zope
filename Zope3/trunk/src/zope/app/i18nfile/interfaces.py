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
$Id: interfaces.py,v 1.3 2004/03/19 03:17:41 srichter Exp $
"""
from zope.i18n.interfaces import II18nAware
from zope.app.file.interfaces import IFile, IImage

class II18nFile(IFile, II18nAware):
    """I18n aware file interface."""

    def removeLanguage(language):
        """Remove translated content for a given language.
        """

class II18nImage(II18nFile, IImage):
    """I18n aware image interface."""

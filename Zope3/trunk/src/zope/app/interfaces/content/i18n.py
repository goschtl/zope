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
"""Interfaces for internationalized versions of content components. 

$Id: i18n.py,v 1.1 2004/02/14 03:27:15 srichter Exp $
"""
from zope.app.content.image import IImage
from zope.app.interfaces.content.file import IFile
from zope.i18n.interfaces import II18nAware


class II18nFile(IFile, II18nAware):
    """I18n aware file interface."""

    def removeLanguage(language):
        '''Remove translated content for a given language.'''


class II18nImage(II18nFile, IImage):
    """I18n aware image interface."""

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

$Id: i18nfile.py,v 1.3 2002/12/31 02:51:59 jim Exp $
"""

from zope.app.interfaces.content.file import IFile
from zope.i18n.interfaces import II18nAware

class II18nFile(IFile, II18nAware):
    """I18n aware file interface."""

    def removeLanguage(language):
        '''Remove translated content for a given language.'''

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
"""Synchronize with Foreign Translation Services

$Id: basetranslationserviceview.py,v 1.2 2002/12/25 14:12:38 jim Exp $
"""

from zope.publisher.browser import BrowserView
from zope.interfaces.i18n import ITranslationService


class BaseTranslationServiceView(BrowserView):

    __used_for__ = ITranslationService


    def getAllLanguages(self):
        """Get all available languages from the Translation Service."""
        return self.context.getAllLanguages()


    def getAllDomains(self):
        return self.context.getAllDomains()

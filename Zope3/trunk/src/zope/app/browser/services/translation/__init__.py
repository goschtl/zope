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
"""Translation Service Views

$Id: __init__.py,v 1.4 2003/08/07 17:41:34 srichter Exp $
"""
from zope.i18n.interfaces import ITranslationService

__metaclass__ = type

class BaseView:

    __used_for__ = ITranslationService

    def getAllLanguages(self):
        """Get all available languages from the Translation Service."""
        return self.context.getAllLanguages()

    def getAllDomains(self):
        """Get all available domains from the Translation Service."""
        return self.context.getAllDomains()

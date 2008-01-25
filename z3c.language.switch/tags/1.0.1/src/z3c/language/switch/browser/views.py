##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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

"""
$Id$
"""
__docformat__ = 'restructuredtext'

import zope.interface
from zope.publisher.browser import BrowserView

from z3c.language.switch import IReadI18n
from z3c.language.switch import IAvailableLanguages


class ContentView(BrowserView):

    zope.interface.implements(IAvailableLanguages)

    def getAvailableLanguages(self):
        """Returns a list of available languages if we provide IReadI18n."""

        if IReadI18n.providedBy(self.context):
            return self.context.getAvailableLanguages()
        else:
            return []


    def hasAvailableLanguages(self):
        """View for to check if we have i18n support on a context."""

        if IReadI18n.providedBy(self.context):
            return True
        else:
            return False

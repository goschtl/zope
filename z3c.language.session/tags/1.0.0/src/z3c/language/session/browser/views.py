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
import zope.component

from zope.publisher.browser import BrowserView

from z3c.language.session import IGetLanguage
from z3c.language.session import IHasLanguage
from z3c.language.session import ILanguageSession
from z3c.language.session import ISetLanguage


class LanguageSessionView(BrowserView):

    zope.interface.implements(IHasLanguage, IGetLanguage, ISetLanguage)

    def hasLanguage(self):
        """View for to check if a session has a i18n language value."""
        try:
            session = ILanguageSession(self.request)
            lang = session.getLanguage()
            if lang:
                return True
            else:
                return False
        except zope.component.ComponentLookupError:
            return False

    def getLanguage(self):
        """View for to check if a session has a i18n language value."""
        _fallback = 'en'
        
        try:
            session = ILanguageSession(self.request)
            return session.getLanguage()
        except AttributeError:
            return _fallback

    def setLanguage(self):
        """Set the given language in the request to the session.
        
        You can do it via the javascript sessionlanguage.js with the
        javascript method setLanguage:
        
        javascript:setLanguage('@@setLanguage','de')
        
        Or send the request to the view '@@setLanguage'. There has to be a 
        variable 'language' and 'nextURL' in the request like
        """
        nextURL = '.'

        if "language" in self.request:
            lang = self.request['language']
        
        if "nextURL" in self.request:
            nextURL = self.request['nextURL']

        if lang:
            session = ILanguageSession(self.request)
            session.setLanguage(lang)

        self.request.response.redirect(nextURL)

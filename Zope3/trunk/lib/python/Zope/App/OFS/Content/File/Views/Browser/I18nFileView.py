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

$Id: I18nFileView.py,v 1.1 2002/06/24 15:44:25 mgedmin Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.I18n.Negotiator import negotiator


class I18nFileView(BrowserView):

    def __call__(self):
        """Call the File"""
        request = self.request
        language = None
        if request is not None:
            langs = self.context.getAvailableLanguages()
            language = negotiator.getLanguage(langs, request)

            request.response.setHeader('Content-Type',
                                       self.context.getContentType())
            request.response.setHeader('Content-Length',
                                       self.context.getSize(language))

        return self.context.getData(language)

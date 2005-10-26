##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Local sites browser views

$Id$
"""
from Products.Five.browser import BrowserView

class LocalSiteView(BrowserView):
    """View for convering a possible site to a site
    """

    def update(self):
        form = self.request.form
        if form.has_key('UPDATE_MAKESITE'):
            self.makeSite()
        elif form.has_key('UPDATE_UNMAKESITE'):
            self.unmakeSite()

    def isSite(self):
        return ISite.providedBy(self.context)

    def makeSite(self):
        """Convert a possible site to a site"""
        if self.isSite():
            raise ValueError('This is already a site')

        enableLocalSiteHook(self.context)
        return "This object is now a site"

    def unmakeSite(self):
        """Convert a site to a possible site"""
        if not self.isSite():
            raise ValueError('This is not a site')

        disableLocalSiteHook(self.context)
        return "This object is no longer a site"

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
"""View Class for the Container's Contents view.

$Id: contents.py 25177 2004-06-02 13:17:31Z jim $
"""

from zope.exceptions import NotFoundError

from zope.app import zapi
from zope.app.size.interfaces import ISized
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.i18n import ZopeMessageIDFactory as _

from ldapauth.interfaces import ILDAPBasedPrincipalSource


class Principals(BrowserView):

    __used_for__ = ILDAPBasedPrincipalSource

    error = ""

    def getPrincipals(self):
        context = self.context
        request = self.request
        try:
            print "START Principals getPrincipals"
            principals = self.context.getPrincipals()
            print "END Principals getPrincipals"
        except :
            principals = []
            self.error = _("Error, No LDAP server or connection found")
        
        return principals

    principals = ViewPageTemplateFile('principals.pt')

    def index(self):
        if 'index.html' in self.context:
            self.request.response.redirect('index.html')
            return ''

        return self._index()

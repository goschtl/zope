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



class CheckConnectionView(BrowserView):

    __used_for__ = ILDAPBasedPrincipalSource


    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context
        self.report = []

    def checkConnection(self):
        """Check connetction to the given LDAP server."""
        report = []

        self._addInfo("Report traceback")

        return self.report

    def _addInfo(self, res):
        """Add traceback info to the report list"""
        self.report.append(res)

    check = ViewPageTemplateFile('checkconnection.pt')

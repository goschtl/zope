##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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

$Id$
"""

from zope.exceptions import NotFoundError

from zope.app import zapi
from zope.app.size.interfaces import ISized
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.i18n import ZopeMessageIDFactory as _

from ldapauth.interfaces import ILDAPBasedPrincipalSource
from ldapauth.interfaces import ICheckLDAPAdapter



class CheckLDAPView(BrowserView):

    __used_for__ = ILDAPBasedPrincipalSource


    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context
        self.report = []

    def getHostInfo(self):
        """Returns a dict with host information."""
        infoDict = {}
        infoDict['host'] = self.context.host
        infoDict['port'] = self.context.port
        infoDict['basedn'] = self.context.basedn
        infoDict['login_attribute'] = self.context.login_attribute
        infoDict['manager_dn'] = self.context.manager_dn
        return infoDict


    def checkConnection(self):
        """Check connetction to the given LDAP server."""
        runtest = self.request.get('runtest', None)
        if runtest == "Run":
            un = self.request.get('username')
            pw = self.request.get('password')
            
            # get the ldapauth source
            testadapter = ICheckLDAPAdapter(self.context)

            # test the connection to the LDAP server
            self._addInfo("<strong>Test python connection and LDAP server binding</strong>")
            self.report = self.report + testadapter.testConnection()
            self._addInfo(" ")

            # test quering the LDAP server
            self._addInfo("<strong>Test get principals</strong>")
            self.report = self.report + testadapter.testGetPrincipals(un)
            self._addInfo(" ")

            # test query the given username

            # test authenticate the given username

            self._addInfo("... more test")
    
            return self.report
        else:
            return ""

    def _addInfo(self, res):
        """Add traceback info to the report list"""
        self.report.append(res)

    check = ViewPageTemplateFile('check.pt')

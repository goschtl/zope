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

$Id: check.py 26680 2004-07-22 16:31:38Z nicoe $
"""

from zope.exceptions import NotFoundError

from zope.app import zapi
from zope.app.size.interfaces import ISized
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.i18n import ZopeMessageIDFactory as _

from ldapadapter.interfaces import IManageableLDAPAdapter
from ldapadapter.interfaces import ICheckLDAPAdapter



class CheckLDAPAdapterView(BrowserView):

    __used_for__ = IManageableLDAPAdapter


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
        infoDict['baseDN'] = self.context.baseDN
        infoDict['bindDN'] = self.context.bindDN
        infoDict['bindPassword'] = self.context.bindPassword
        return infoDict


    def checkConnection(self):
        """Check connetction to the given LDAP server."""
        runtest = self.request.get('runtest', None)
        if runtest == "Run":
            dn = self.request.get('bindDN')
            pw = self.request.get('bindPassword')
            
            # get the ldapauth source
            testadapter = ICheckLDAPAdapter(self.context)

            # test the connection to the LDAP server
            self._addInfo("<strong>Test python connection and LDAP server binding</strong>")
            self.report = self.report + testadapter.testConnection(dn, pw)
            self._addInfo("<strong>Tests done</strong>")
            self._addInfo(" ")
    
            return self.report
        else:
            return ""

    def _addInfo(self, res):
        """Add traceback info to the report list"""
        self.report.append(res)

    check = ViewPageTemplateFile('check.pt')

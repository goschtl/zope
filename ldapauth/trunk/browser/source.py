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
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.size.interfaces import ISized
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.i18n import ZopeMessageIDFactory as _

from ldapauth.interfaces import ILDAPBasedPrincipalSource
from ldapauth.interfaces import ILDAPManager


class PrincipalSource(BrowserView):

    __used_for__ = ILDAPBasedPrincipalSource

    error = ""

    def getUserInfos(self):
        context = self.context
        request = self.request
        infoList = []
        try:
            principals = self.context.getPrincipals(name='')
        except :
            principals = []
            self.error = _("Error, No LDAP server or connection found")
        
        for principal in principals:
            info = removeSecurityProxy(principal)
            zmi_icon = zapi.queryView(info, 'zmi_icon', request)
            entry = {}
            if zmi_icon is None:
                entry['icon'] = None
            else:
                entry['icon'] = zmi_icon()
            entry['login'] = info.getLogin()
            entry['title'] = info.title
            entry['description'] = info.description
            infoList.append(entry)
        
        return infoList


    def getLoginAttribute(self):
        context = self.context
        try:
            return context.login_attribute
        except:
            return "Lookup Error"


    contents = ViewPageTemplateFile('source.pt')



class PrincipalSourceManager(PrincipalSource):

    __used_for__ = ILDAPManager

    error = ""

    def getUserInfos(self):
        context = self.context
        request = self.request
        infoList = []
        try:
            principals = self.context.getPrincipals(name='')
        except :
            principals = []
            self.error = _("Error, No LDAP server or connection found")
        
        for principal in principals:
            info = removeSecurityProxy(principal)
            zmi_icon = zapi.queryView(info, 'zmi_icon', request)
            entry = {}
            if zmi_icon is None:
                entry['icon'] = None
            else:
                entry['icon'] = zmi_icon()
            entry['url'] = info.id
            entry['login'] = info.getLogin()
            entry['title'] = info.title
            entry['description'] = info.description
            infoList.append(entry)
        
        return infoList


    manager = ViewPageTemplateFile('manager.pt')

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
"""Synchronisation view

$Id: sync.py $
"""

from zope.security.proxy import trustedRemoveSecurityProxy

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.i18n import ZopeMessageIDFactory as _

from ldapauth.interfaces import ILDAPBasedPrincipalSource



class SyncLDAPView(BrowserView):

    __used_for__ = ILDAPBasedPrincipalSource

    error = ""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getHostInfo(self):
        """Returns a dict with host information."""
        infoDict = {}
        infoDict['host'] = self.context.host
        infoDict['port'] = self.context.port
        infoDict['basedn'] = self.context.basedn
        infoDict['login_attribute'] = self.context.login_attribute
        infoDict['manager_dn'] = self.context.manager_dn
        return infoDict

    def loadPrincipalFromLDAP(self):
        """Get all principals from the LDAP server and add it to the cache."""
        runtest = self.request.get('runsync', None)
        if runtest == "Run":
            trace = self.request.get("trace", None)
            try:
                principals = self.context.getPrincipals(name='')
            except:
                msg = _("Error during the synchronisation from the LDAP server.")
                self.error = msg
    
            if trace != None:
                infoList = []
                counter = len(principals)
                infoList.append("""%s principals form LDAP server successfully synchronized!
                                """ % counter
                               )
                for principal in principals:
                    info = trustedRemoveSecurityProxy(principal)
                    entry = "%s, %s, %s" % (info.getLogin(), info.title, info.description)
                    infoList.append(entry)
            
                return infoList
            else:
                counter = len(principals)
                return ["""%s principals form LDAP server successfully synchronized!
                        """ % counter
                       ]
        else:
            return None

    sync = ViewPageTemplateFile('sync.pt')

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
"""A plugable authentication module for LDAP.

$Id: check.py 27204 2004-08-21 01:46:57Z nicoe $
"""

from zope.security.proxy import removeSecurityProxy
from zope.interface import implements

from interfaces import ICheckLDAPAdapter

class CheckLDAPAdapter:
    """A LDAP connection test adapter."""

    implements(ICheckLDAPAdapter)

    def __init__(self, context):
        self.context = context
        self.report = []
    
    def testConnection(self, bindDN, bindPassword):
        self.report = []
        adapter = removeSecurityProxy(self.context)
        self.report.append("Start check connection")
        
        try:
            self.report.append("... try connect with:")
            self.report.append("... bindDN = %s" % bindDN)
            self.report.append("... bindPassword = %s" % bindPassword)
            
            connection = adapter.connect(bindDN, bindPassword)
            
            if connection != None:
                self.report.append("... <strong>Connecting failed!</strong>")
            else:
                self.report.append("... <strong>OK!</strong>")
            
            return report

        except:
            self.report.append("... <strong>Test failed!</strong>")
            return self.report

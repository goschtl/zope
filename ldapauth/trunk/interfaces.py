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
"""A plugable authentication module for LDAP.

$Id$
"""
from zope.interface import Interface

from zope.schema import TextLine, Int, List, Password
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.pluggableauth.interfaces import IPrincipalSource

class ILDAPBasedPrincipalSource(IPrincipalSource):
    """Describe LDAP-based authentication sources."""

    host = TextLine(
            title = _(u'Hostname'),
            description = _(u'LDAP Server location'),
            default = u'localhost')

    port = Int(
            title = _(u'Port'),
            description = _(u'LDAP Server Port'),
            default = 389)

    basedn = TextLine(
            title = _(u'Base DN'),
            description = _(u'Base of the distinguished name'))

    login_attribute = TextLine(
            title = _(u'Login attribut name'),
            description = _(u'LDAP attribute used as login name'))

    manager_dn = TextLine(
            title = _(u'Manager DN'),
            description = _(u'Manager DN used to bind to the server'))

    manager_passwd = Password(
            title = _(u'Manager password'),
            description = _(u"Manager's password"))



class ILDAPTestAdapter(Interface):
    """A test adapter for to test the connection between Zope and LDAP."""

    def testConnection():
        """Returns a report about connecting the LDAP server.
        
        Each step of connecting the server is reported as a string
        in a report (list).
        """

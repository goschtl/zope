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
"""LDAP Adapter interfaces.

$Id$
"""
from zope.interface import Interface
from zope.interface import Attribute
from zope.schema import Int
from zope.schema import Bool
from zope.schema import TextLine

from zope.app.i18n import ZopeMessageIDFactory as _


class ILDAPAdapter(Interface):
    """Adapter to an LDAP server."""
    serverUrl = TextLine(
        title=_("Server URL"),
        description=_(
            "Specify the LDAP URL of the server. Examples:\n"
            "\n"
            "ldap:///\n",
            "ldap://localhost:389/\n",
            ),
        default=u"ldap://localhost",
        required=True,
        )
    host = TextLine(
        title=_("Host"),
        default=u'localhost',
        required=True,
        )
    port = Int(
        title=_("Port"),
        default=389,
        required=True,
        )
    useSSL = Bool(
        title=_("Use SSL"),
        default=False,
        )

    def connect(dn, password):
        """Connect to the server.

        Returns an ILDAPConnection.
        """


class ILDAPConnection(Interface):
    """LDAP connection to a server, bound to a user."""
    def search(base, scope='one', filter='(objectclass=*)', attrs=None):
        """Search an LDAP server.

        - base is a unicode dn.

        - scope is 'base, 'one' or 'sub'.

        - filter is a unicode LDAP filter (rfc2254).

        - attrs may be a list of entry attributes to return, or None to
          return them all.

        Returns a sequence of (dn, entry), where dn is unicode and entry
        is a mapping whose values are lists of unicode strings.

        May raise ldap exceptions.
        """
        # TODO: some values are binary and should not be converted to unicode

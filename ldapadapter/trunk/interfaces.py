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
    bindDN = TextLine(
        title=_("Bind DN"),
        default=u'',
        )
    bindPassword = TextLine(
        title=_("Bind password"),
        default=u'',
        )
    useSSL = Bool(
        title=_("Use SSL"),
        default=False,
        )

    def connect(dn, password=None):
        """Connect to the server.

        Returns an ILDAPConnection.
        """

class ILDAPAdapterManagement(Interface):
    serverURL = TextLine(
        title=_("Server URL"),
        description=_(
            "Specify the LDAP URL of the server. Examples:\n"
            "\n"
            "ldap:///\n",
            "ldaps://localhost:389/\n",
            ),
        default=u"ldap://localhost",
        )
    bindDN = TextLine(
        title=_("Bind DN"),
        default=u'',
        )
    bindPassword = TextLine(
        title=_("Bind password"),
        default=u'',
        )

class IManageableLDAPAdapter(ILDAPAdapter,
                             ILDAPAdapterManagement):
    """LDAP Adapter with management functions."""


class ILDAPConnection(Interface):
    """LDAP connection to a server, bound to a user."""

    def add(dn, entry):
        """Add an entry.

        - dn is a unicode dn.

        - entry is a mapping whose values are lists.
        """

    def delete(dn):
        """Delete an entry.

        dn is a unicode dn.
        """

    def modify(dn, entry):
        """Modify an entry.

        - dn is a unicode dn.

        - entry is the subset of attributes we want to modify.
        """

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

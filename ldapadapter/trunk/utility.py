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
"""LDAP Adapter utility.

$Id$
"""

import re
import ldap
from ldap import OPT_PROTOCOL_VERSION
from ldap import VERSION3
from ldap import SCOPE_BASE
from ldap import SCOPE_ONELEVEL
from ldap import SCOPE_SUBTREE
from ldap import MOD_ADD
from ldap import MOD_REPLACE
from ldap import MOD_DELETE

from persistent import Persistent

from zope.interface import implements
from zope.app.container.contained import Contained

from exceptions import LDAPURIParseError
from exceptions import LDAP_uri_parse_error

from interfaces import ILDAPAdapter
from interfaces import ILDAPConnection
from interfaces import IManageableLDAPAdapter

SCOPES = {'base': SCOPE_BASE,
          'one': SCOPE_ONELEVEL,
          'sub': SCOPE_SUBTREE,
          }
def convertScope(scope):
    return SCOPES[scope]


def valuesToUTF8(values):
    return [v.encode('utf-8') for v in values]


class LDAPAdapter(object):
    implements(ILDAPAdapter)

    def __init__(self, host='localhost', port=389, useSSL=False,
                 bindDN='', bindPassword=''):
        self.host = host
        self.port = port
        self.useSSL = useSSL
        self.bindDN = bindDN
        self.bindPassword = bindPassword

    def connect(self, dn=None, password=None):
        conn_str = self.getServerURL()
        conn = ldap.initialize(conn_str)
        try:
            conn.set_option(OPT_PROTOCOL_VERSION, VERSION3)
        except LDAPError:
            # TODO: fallback on VERSION2 and note that the values
            # are then not utf-8 encoded (charset is implicit (?))
            raise Exception("Server should be LDAP v3")
        # TODO: conn.set_option(OPT_REFERRALS, 1)

        # Bind the connection to the dn
        if dn is None:
            dn = self.bindDN
            password = self.bindPassword
        conn.simple_bind_s(dn, password)
        # May raise INVALID_CREDENTIALS, SERVER_DOWN, ...

        return LDAPConnection(conn)

    def getServerURL(self):
        """Get the server LDAP URL from the server info."""
        proto =  self.useSSL and 'ldaps' or 'ldap'
        return '%s://%s:%s' % (proto, self.host, self.port)


class LDAPConnection(object):
    implements(ILDAPConnection)

    def __init__(self, conn):
        self.conn = conn

    def add(self, dn, entry):
        attrs_list = []
        for key, values in entry.items():
            attrs_list.append((key, valuesToUTF8(values)))
        self.conn.add_s(dn.encode('utf-8'), attrs_list)

    def delete(self, dn):
        self.conn.delete_s(dn.encode('utf-8'))

    def modify(self, dn, entry):
        # Get current entry
        res = self.search(dn, 'base')
        if not res:
            raise Exception("No such entry") # FIXME use proper exception
        cur_dn, cur_entry = res[0]

        mod_list = []
        for key, values in entry.items():
            if cur_entry.has_key(key):
                if values == []:
                    # TODO fail on rdn removal
                    mod_list.append((MOD_DELETE, key, None))
                elif cur_entry[key] != values:
                    # TODO treat modrdn
                    mod_list.append((MOD_REPLACE, key, valuesToUTF8(values)))
            else:
                if values != []:
                    mod_list.append((MOD_ADD, key, valuesToUTF8(values)))
        if not mod_list:
            return

        self.conn.modify_s(dn.encode('utf-8'), mod_list)

    def search(self, base, scope='sub', filter='(objectClass=*)',
               attrs=None):
        # Convert from unicode to utf-8.
        base = base.encode('utf-8')
        scope = convertScope(scope)
        # XXX convert filter to utf-8
        ldap_entries = self.conn.search_s(base, scope, filter, attrs)
        # May raise NO_SUCH_OBJECT, SERVER_DOWN, SIZELIMIT_EXCEEDED

        # Convert returned values from utf-8 to unicode.
        results = []
        for dn, entry in ldap_entries:
            dn = unicode(dn, 'utf-8')
            for key, values in entry.items():
                # TODO: Can key be non-ascii? Check LDAP spec.
                # FIXME: there may be non-textual binary values.
                values[:] = [unicode(v, 'utf-8') for v in values]
            results.append((dn, entry))
        return results


class ManageableLDAPAdapter(LDAPAdapter, Persistent, Contained):
    """LDAP adapter utility
    """
    implements(IManageableLDAPAdapter)

    def _setServerURL(self, url):
        """Set the server info from an LDAP URL.

        An LDAP url is of the form ldap[s]://host:port
        """
        port = 389
        url = url.strip()
        urlList = url.split(':')
        if len(urlList) >= 2:
            useSSL = urlList[0].endswith('s')
            host = urlList[1][2:]
            if len(urlList) == 3:
                port = int(urlList[2])
        else:
            LDAPURIParseError(LDAP_uri_parse_error)

        self.host = host
        self.port = port
        self.useSSL = useSSL

    serverURL = property(LDAPAdapter.getServerURL, _setServerURL)

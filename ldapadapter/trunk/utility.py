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

import ldap
from ldap import OPT_PROTOCOL_VERSION
from ldap import VERSION3
from ldap import SCOPE_BASE
from ldap import SCOPE_ONELEVEL
from ldap import SCOPE_SUBTREE

from persistent import Persistent

from zope.interface import implements
from zope.app.container.contained import Contained

from interfaces import ILDAPAdapter
from interfaces import ILDAPConnection

SCOPES = {'base': SCOPE_BASE,
          'one': SCOPE_ONELEVEL,
          'sub': SCOPE_SUBTREE,
          }
def convertScope(scope):
    return SCOPES[scope]

class LDAPAdapter(object):
    implements(ILDAPAdapter)

    def __init__(self, host='localhost', port=389, useSSL=False):
        self.host = host
        self.port = port
        self.useSSL = useSSL

    def connect(self, dn, password=None):
        proto = self.useSSL and 'ldaps' or 'ldap'
        conn_str = '%s://%s:%s/' % (proto, self.host, self.port)
        conn = ldap.initialize(conn_str)
        try:
            conn.set_option(OPT_PROTOCOL_VERSION, VERSION3)
        except LDAPError:
            # TODO: fallback on VERSION2 and note that the values
            # are then not utf-8 encoded (charset is implicit (?))
            raise Exception("Server should be LDAP v3")
        # TODO: conn.set_option(OPT_REFERRALS, 1)

        # Bind the connection to the dn
        conn.simple_bind_s(dn, password)
        # May raise INVALID_CREDENTIALS, SERVER_DOWN, ...

        return LDAPConnection(conn)


class LDAPConnection(object):
    implements(ILDAPConnection)

    def __init__(self, conn):
        self.conn = conn

    def add(self, dn, entry):
        attrs_list = entry.items()
        dn = dn.encode('utf-8')
        self.conn.add_s(dn, attrs_list)

    def delete(self, dn):
        dn = dn.encode('utf-8')
        self.conn.del_s(dn)

    def modify(self, dn, entry):
        # Get current entry
        pass

    def search(self, base, scope='sub', filter='(objectClass=*)',
               attrs=None):
        # Convert from unicode to utf-8.
        base = base.encode('utf-8')
        scope = convertScope(scope)
        # XXX convert filter
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


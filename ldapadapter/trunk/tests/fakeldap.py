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
"""Fake LDAP module to test simple functionnality.

$Id$
"""

import sha
import base64
from copy import deepcopy

import ldap
from ldap import OPT_PROTOCOL_VERSION
from ldap import VERSION3
from ldap import SCOPE_BASE
from ldap import SCOPE_ONELEVEL
from ldap import SCOPE_SUBTREE
from ldap import MOD_ADD
from ldap import MOD_DELETE
from ldap import MOD_REPLACE

class INVALID_CREDENTIALS(Exception): pass
class ALREADY_EXISTS(Exception): pass
class NO_SUCH_OBJECT(Exception): pass
#class SERVER_DOWN(Exception): pass
#class SIZELIMIT_EXCEEDED(Exception): pass


the_data = {}
# Data is a mapping of {dnl -> entry}, dnl is a tuple of rdns

explode_dn = ldap.explode_dn


class FakeLDAPObject(object):

    def __init__(self):
        pass

    def set_option(self, option, value):
        pass

    def simple_bind_s(self, dn, password):
        if dn.find('Manager') >= 0:
            return 1

        results = self.search_s(dn)
        pwd = None
        for key, values in results:
            if key == 'userPassword':
                pwd = values[0]
                break

        if pwd is None:
            raise INVALID_CREDENTIALS

        # Check password encoding
        if pwd.startswith('{SHA}'):
            s = sha.new(password)
            enc = '{SHA}' + base64.encodestring(s.digest())
        else:
            enc = password

        if pwd != enc:
            raise INVALID_CREDENTIALS

        return 1

    def add_s(self, dn, attr_list):
        dnl = tuple(dn.split(','))
        if dnl in the_data:
            raise ALREADY_EXISTS
        entry = {}
        for key, values in attr_list:
            entry[key] = values
        the_data[dnl] = entry

    def delete_s(self, dn):
        dnl = tuple(dn.split(','))
        if dnl not in the_data:
            raise NO_SUCH_OBJECT
        del the_data[dnl]

    def search_s(self, base, scope=SCOPE_SUBTREE, filter='(objectClass=*)',
                 attrs=[]):
        basel = tuple(base.split(','))
        basellen = len(basel)

        # Analyze the filter, assume simple query
        orig_filter = filter
        if not filter.startswith('(') or not filter.endswith(')'):
            raise ValueError("Illegal filter syntax %s" % orig_filter)
        filter = filter[1:-1]

        # Assume simple filter
        fkey, fval = filter.split('=')
        if not fval:
            raise ValueError("Illegal filter syntax %s" % orig_filter)

        # Make objectclass=* work even on simple debug objects.
        match_all = (filter.lower() == 'objectclass=*')

        # Iterate on all entries and do the search
        res = []
        #import pdb; pdb.set_trace()
        for dnl, entry in the_data.iteritems():
            if dnl[-basellen:] != basel:
                continue
            dnllen = len(dnl)
            if not ((scope == SCOPE_SUBTREE) or
                    (scope == SCOPE_ONELEVEL and dnllen == basellen+1) or
                    (scope == SCOPE_BASE and dnllen == basellen)):
                continue
            # Check filter match.
            if not entry.has_key(fkey) and not match_all:
                continue
            values = entry.get(fkey, [])
            ok = 0
            if fval == '*' or match_all:
                ok = 1
            elif fval[0] == '*' and fval[-1] == '*':
                fval = fval[1:-1]
                for v in values:
                    if fval in v:
                        ok = 1
                        break
            elif fval[0] == '*':
                fval = fval[1:]
                for v in values:
                    if v.endswith(fval):
                        ok = 1
                        break
            elif fval[-1] == '*':
                fval = fval[:-1]
                for v in values:
                    if v.startswith(fval):
                        ok = 1
                        break
            else:
                for v in values:
                    if fval == v:
                        ok = 1
                        break
            if not ok:
                continue
            dn = ','.join(dnl)
            res.append((dn, deepcopy(entry)))
        return res

    def modify_s(self, dn, mod_list):
        dnl = tuple(dn.split(','))
        entry = the_data.get(dnl)
        if entry is None:
            raise NO_SUCH_OBJECT
        for op, key, values in mod_list:
            if op == MOD_ADD:
                if not entry.has_key(key):
                    if not values:
                        raise ValueError("Illegal MOD_ADD of nothing")
                    entry[key] = []
                cur = entry[key]
                for v in values:
                    if v not in cur:
                        cur.append(v)
            elif op == MOD_DELETE:
                if not entry.has_key(key):
                    raise NO_SUCH_OBJECT # FIXME find real exception
                if not values:
                    cur = []
                else:
                    cur = entry[key]
                    for v in values:
                        try:
                            cur.remove(v)
                        except ValueError:
                            raise NO_SUCH_OBJECT # FIXME
                if not cur:
                    del entry[key]
            else: # op == MOD_REPLACE
                if values:
                    entry[key] = values
                elif entry.has_key(key):
                    del entry[ley]

def initialize(conn_str):
    """Initialize."""
    return FakeLDAPObject()


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
# FOR A PARTICULAR PURPOSE
#
# FakeLDAP      Fake LDAP interface to test LDAP functionality
#               independently of a running LDAP server
#
# This software is governed by a license (ZPL v2.1).
# (c) Jens Vagelpohl, Nicolas Évrard
##############################################################################
"""LDAPAdapter test packages.

$Id: $
"""

__version__='$Revision: 1.7 $'[11:-2]

import ldap, sha, base64, copy
from ldap.modlist import addModlist

# Module-level stuff
__version__ = '2.fake'

SCOPE_BASE = getattr(ldap, 'SCOPE_BASE')
SCOPE_ONELEVEL = getattr(ldap, 'SCOPE_ONELEVEL')
SCOPE_SUBTREE = getattr(ldap, 'SCOPE_SUBTREE')

MOD_ADD = getattr(ldap, 'MOD_ADD')
MOD_REPLACE = getattr(ldap, 'MOD_REPLACE')
MOD_DELETE = getattr(ldap, 'MOD_DELETE')

OPT_PROTOCOL_VERSION = None
OPT_REFERRALS = None
VERSION2 = None
VERSION3 = None

class LDAPError(Exception): pass
class SERVER_DOWN(Exception): pass
class PROTOCOL_ERROR(Exception): pass
class NO_SUCH_OBJECT(Exception): pass
class INVALID_CREDENTIALS(Exception): pass
class ALREADY_EXISTS(Exception): pass
class SIZELIMIT_EXCEEDED(Exception): pass
class PARTIAL_RESULTS(Exception): pass

REFERRAL = None

TREE = {}


def initialize(conn_str):
    """ Initialize a new connection """
    return FakeLDAPConnection()

def explode_dn(dn, *ign, **ignored):
    """ Get a DN's elements """
    return [x.strip() for x in dn.split(',')]

def clearTree():
    TREE.clear()

def addTreeItems(dn):
    """ Add structure directly to the tree given a DN """
    elems = explode_dn(dn)
    elems.reverse()
    tree_pos = TREE

    for elem in elems:
        if not tree_pos.has_key(elem):
            tree_pos[elem] = {}

        tree_pos = tree_pos[elem]

def sha_encode(paswd):
    sha_pswd = sha.new(paswd)
    sha_dig = sha_pswd.digest()
    paswd_enc = base64.encodestring(sha_dig).strip()
    return '{SHA}%s' % paswd_enc

class modlist:

    addModlist = addModlist

class FakeLDAPConnection:
    
    def __init__(self):
        pass

    def set_option(self, option, value):
        pass

    def simple_bind_s(self, binduid, bindpwd):
        if binduid.find('Manager') != -1:
            return 1

        if bindpwd == '':
            # Emulate LDAP mis-behavior
            return 1

        enc_bindpwd = bindpwd
        rec = self.search_s(binduid)
        rec_pwd = ''
        for key, val_list in rec:
            if key == 'userPassword':
                rec_pwd = val_list[0]
                break

        if not rec_pwd:
            raise INVALID_CREDENTIALS

        if enc_bindpwd == rec_pwd:
            return 1
        else:
            raise INVALID_CREDENTIALS


    def search_s(self, base, scope=SCOPE_SUBTREE, query='(objectClass=*)', attrs=[]):
        elems = explode_dn(base)
        elems.reverse()
        tree_pos = TREE

        for elem in elems:
            if tree_pos.has_key(elem):
                tree_pos = tree_pos[elem]

        if query == '(objectClass=*)':
            if scope == SCOPE_BASE and tree_pos.get('dn', '') == base:
                return (([base, tree_pos],))
            else:
                return tree_pos.items()

        if query.find('objectClass=groupOfUniqueNames') != -1:
            res = []
            if query.find('uniqueMember=') == -1:
                for key, vals in tree_pos.items():
                    res.append(('%s,%s' % (key, base), vals))

            else:
                q_start = query.find('uniqueMember=') + 13
                q_end = query.find(')', q_start)
                q_val = query[q_start:q_end]
                
                for key, val in tree_pos.items():
                    if ( val.has_key('uniqueMember') and 
                         q_val in val['uniqueMember'] ):
                        res.append(('%s,%s' % (key, base), val))

            return res

        elif query.find('unique') != -1:
            res = []
            if query.find('*') != -1:
                for key, vals in tree_pos.items():
                    res.append(('%s,%s' % (key, base), vals))
            else:
                q_start = query.lower().find('uniquemember=') + 13
                q_end = query.find(')', q_start)
                q_val = query[q_start:q_end]

                for key, val in tree_pos.items():
                    if ( val.has_key('uniqueMember') and
                         q_val in val['uniqueMember'] ):
                        res.append(('%s,%s' % (key, base), val))

            return res
 

        else:
            res = []
            if query.startswith('('):
                query = query[1:]

            if query.endswith(')'):
                query = query[:-1]

            if query.startswith('&'):
               # Convoluted query, gotta take it apart
               query = query[2:]
               query = query[:-1]
               query_elems = query.split(')(')
               query = query_elems[0]
               query_elems.remove(query)

            q_key, q_val = query.split('=')
            for key, val in tree_pos.items():
                if val.has_key(q_key):
                    if '*' not in q_val and q_val in val[q_key]:
                        res.append(('%s,%s' % (key, base), val))
                    elif '*' == q_val[0] and '*' == q_val[-1]:
                        qval = q_val[1:-1]
                        for value in val[q_key]:
                            if qval in value:
                                res.append(('%s,%s' % (key, base), val))
                    elif '*' == q_val[0]:
                        qval = q_val[1:]
                        for values in val[q_key]:
                            if value.endswith(qval):
                                res.append(('%s,%s' % (key, base), val))
                    elif '*' == q_val[-1]:
                        qval = q_val[:-1]
                        for values in val[q_key]:
                            if value.startswith(qval):
                                res.append(('%s,%s' % (key, base), val))

            return res

    def add_s(self, dn, attr_list):
        elems = explode_dn(dn)
        elems.reverse()
        rdn = elems[-1]
        base = elems[:-1]
        tree_pos = TREE

        for elem in base:
            if tree_pos.has_key(elem):
                tree_pos = tree_pos[elem]

        if tree_pos.has_key(rdn):
            raise ALREADY_EXISTS
        else:
            tree_pos[rdn] = {}
            rec = tree_pos[rdn]

            for key, val in attr_list:
                if isinstance(val, list):
                    rec[key] = val
                else:
                    rec[key] = [val]

    def delete_s(self, dn):
        elems = explode_dn(dn)
        elems.reverse()
        rdn = elems[-1]
        base = elems[:-1]
        tree_pos = TREE

        for elem in base:
            if tree_pos.has_key(elem):
                tree_pos = tree_pos[elem]

        if tree_pos.has_key(rdn):
            del tree_pos[rdn]

    def modify_s(self, dn, mod_list):
        elems = explode_dn(dn)
        elems.reverse()
        rdn = elems[-1]
        base = elems[:-1]
        tree_pos = TREE

        for elem in base:
            if tree_pos.has_key(elem):
                tree_pos = tree_pos[elem]

        rec = copy.deepcopy(tree_pos.get(rdn))

        for mod in mod_list:
            if mod[0] == MOD_REPLACE:
                rec[mod[1]] = mod[2]
            elif mod[0] == MOD_ADD:
                cur_val = rec[mod[1]]
                cur_val.extend(mod[2])
                rec[mod[1]] = cur_val
            else:
                if rec.has_key(mod[1]):
                    cur_vals = rec[mod[1]]
                    for removed in mod[2]:
                        if removed in cur_vals:
                            cur_vals.remove(removed)

                    rec[mod[1]] = cur_vals

        tree_pos[rdn] = rec

    def modrdn_s(self, dn, new_rdn, *ign):
        elems = explode_dn(dn)
        elems.reverse()
        rdn = elems[-1]
        base = elems[:-1]
        tree_pos = TREE

        for elem in base:
            if tree_pos.has_key(elem):
                tree_pos = tree_pos[elem]

        rec = tree_pos.get(rdn)
        
        del tree_pos[rdn]
        tree_pos[new_rdn] = rec


class ldapobject:
    class ReconnectLDAPObject(FakeLDAPConnection):
        def __init__(self, *ignored):
            pass

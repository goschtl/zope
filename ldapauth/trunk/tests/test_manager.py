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
"""Test for the management of LDAP users

$Id$
"""
import sys
from unittest import TestCase, TestSuite, makeSuite, main

import FakeLDAP
if sys.modules.has_key('_ldap'):
    del sys.modules['_ldap']
sys.modules['ldap'] = FakeLDAP

import ldap

from zope.exceptions import NotFoundError
from zope.app.pluggableauth import SimplePrincipal

from ldapauth.source import LDAPPrincipalSource
from ldapauth.manager import LDAPManagerAdapter

class LDAPManagerAdapterTest(TestCase):

    def setUp(self):
        self.conn = ldap.initialize('ldap://localhost:389')
        self.conn.simple_bind_s('cn=Manager,dc=fake', 'root')
        try:
            self.conn.add_s('uid=toto_l,ou=people,dc=fake',
                    (('uid', 'toto_l'),
                     ('userPassword', 'toto_p')))
            self.conn.add_s('uid=tata_l,ou=people,dc=fake',
                    (('uid', 'tata_l'),
                     ('userPassword', 'tata_p')))
            self.conn.add_s('uid=titi_l,ou=people,dc=fake',
                    (('uid', 'titi_l'),
                     ('userPassword', 'titi_p')))
        except ldap.ALREADY_EXISTS:
            pass

        self.toto = SimplePrincipal('toto_l', 'toto_p')
        self.tutu = SimplePrincipal('tutu_l', 'tutu_p')

        self.source = LDAPPrincipalSource(
                'localhost', 389, 'ou=people,dc=fake',
                'uid', 'cn=Manager,dc=fake', 'root')

    def test_addPrincipal(self):
        manager = LDAPManagerAdapter(self.source)
        manager.addPrincipal(self.tutu)
        tutu = self.source.getPrincipal('\t\ttutu_l')
        self.assertEquals('tutu_l', tutu.login)
        rs = self.conn.search_s('ou=people,dc=fake', query='(uid=tutu_l)')
        self.assertEquals(len(rs), 1)

    def test_editPrincipal(self):
        pass

    def test_deletePrincipal(self):
        manager = LDAPManagerAdapter(self.source)
        manager.deletePrincipal(self.toto)
        self.assertRaises(NotFoundError, self.source.getPrincipal, '\t\ttoto_l')
        rs = self.conn.search_s('ou=people,dc=fake', query='(uid=toto_l)')
        self.assertEquals(len(rs), 0)

def test_suite():
    return TestSuite((
        makeSuite(LDAPManagerAdapterTest),))

if __name__ == '__main__' :
    main(defaultTest='test_suite')

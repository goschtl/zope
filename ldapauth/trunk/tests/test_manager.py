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
from ldapauth.source import LDAPPrincipalSource
from ldapauth.manager import LDAPManagerAdapter

class LDAPManagerAdapterTest(TestCase):

    def setUp(self):
        l = ldap.initialize('ldap://localhost:389')
        l.simple_bind_s('cn=Manager,dc=fake', 'root')
        try:
            l.add_s('uid=toto_l,ou=people,dc=fake',
                    (('uid', 'toto_l'),
                     ('userPassword', 'toto_p')))
            l.add_s('uid=tata_l,ou=people,dc=fake',
                    (('uid', 'tata_l'),
                     ('userPassword', 'tata_p')))
            l.add_s('uid=titi_l,ou=people,dc=fake',
                    (('uid', 'titi_l'),
                     ('userPassword', 'titi_p')))
        except ldap.ALREADY_EXISTS:
            pass

        self.source = LDAPPrincipalSource(
                'localhost', 389, 'ou=people,dc=fake',
                'uid', 'cn=Manager,dc=fake', 'root')

    def test_addPrincipal(self):
        pass

    def test_editPrincipal(self):
        pass

    def test_deletePrincipal(self):
        pass

def test_suite():
    return TestSuite((
        makeSuite(LDAPManagerAdapterTest),))

if __name__ == '__main__' :
    main(defaultTest='test_suite')

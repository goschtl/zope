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

$Id:
"""

import sys
from unittest import TestCase, TestSuite, makeSuite, main

# FakeLDAP taken from LDAPUserFolder of Jens Vagelpohl
import FakeLDAP
if sys.modules.has_key('_ldap'):
    del sys.modules['_ldap']
sys.modules['ldap'] = FakeLDAP

import ldap
from ldapauth.source import LDAPPrincipalSource
from zope.exceptions import NotFoundError

class LDAPPrincipalSourceTest(TestCase):
    
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

    def test_getPrincipal(self):
        toto = self.source.getPrincipal('\t\ttoto_l')
        self.assertEqual(toto.password, 'toto_p')
        self.assertEqual(toto.login, 'toto_l')
        self.assertRaises(NotFoundError, self.source.getPrincipal, '\t\tmoo')

    def test_getPrincipals(self):
        users = self.source.getPrincipals('t')
        self.assertEquals(len(users), 3)
        for user in users:
            self.assert_('t' in user.login)
        self.assertEquals(len(self.source.getPrincipals('ta')), 1)

    def test_authenticate(self):
        self.assertEquals(self.source.authenticate('toto_l', 'toto_p').login,
                'toto_l')
        self.assertEquals(self.source.authenticate('toto_l', 'toto_p').password,
                'toto_p')
        self.assertEquals(self.source.authenticate('toto_l', 'toto'), None)
        self.assertEquals(self.source.authenticate('toto', 'toto'), None)

def test_suite():
    return TestSuite((
        makeSuite(LDAPPrincipalSourceTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

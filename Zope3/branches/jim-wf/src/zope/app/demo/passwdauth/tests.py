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
"""/etc/passwd Authentication Plugin Tests

$Id$
"""
import os
from zope.app.demo import passwdauth
from zope.app.security.interfaces import PrincipalLookupError
from unittest import TestCase, main, makeSuite

class PasswdPrincipalSourceTest(TestCase):

    def setUp(self):
        dir = os.path.dirname(passwdauth.__file__)
        self.source = passwdauth.PasswdPrincipalSource(
            os.path.join(dir, 'passwd.sample'))

    def test_getPrincipal(self):
        self.assertEqual(self.source.getPrincipal('\t\tfoo1').password, 'bar1')
        self.assertEqual(self.source.getPrincipal('\t\tfoo2').password, 'bar2')
        self.assertRaises(PrincipalLookupError, self.source.getPrincipal, '\t\tfoo')

    def test_getPrincipals(self):
        self.assertEqual(len(self.source.getPrincipals('foo')), 2)
        self.assertEqual(len(self.source.getPrincipals('')), 2)
        self.assertEqual(len(self.source.getPrincipals('2')), 1)

    def test_authenticate(self):
        self.assertEqual(self.source.authenticate('foo1', 'bar1')._id, 'foo1')
        self.assertEqual(self.source.authenticate('foo1', 'bar'), None)
        self.assertEqual(self.source.authenticate('foo', 'bar'), None)
    
def test_suite():
    return makeSuite(PasswdPrincipalSourceTest)
    
if __name__=='__main__':
    main(defaultTest='test_suite')
    

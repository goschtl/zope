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
"""LDAPAdapter tests

$Id$
"""
__docformat__ = "reStructuredText"
import sys
import unittest
from zope.testing import doctest
from zope.app.tests import placelesssetup, ztapi
from zope.app.event.tests.placelesssetup import getEvents


def setUp(test):
    import fakeldap
    if sys.modules.has_key('_ldap'):
        test.old_ldap = sys.modules['_ldap']
        del sys.modules['_ldap']
    else:
        test.old_ldap = None
    sys.modules['_ldap'] = fakeldap

def tearDown(test):
    del sys.modules['_ldap']
    if test.old_ldap is not None:
        sys.modules['_ldap'] = test.old_ldap

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt',
                             setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


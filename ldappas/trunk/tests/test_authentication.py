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
"""LDAP PAS Plugins tests

$Id$
"""

import sys
import unittest
from zope.testing import doctest

from zope.interface import implements
from zope.app import zapi
from zope.app.tests import setup
from zope.app.servicenames import Utilities
from zope.app.utility import LocalUtilityService

from ldapadapter.interfaces import ILDAPAdapter
from ldapadapter.exceptions import ServerDown
from ldapadapter.exceptions import InvalidCredentials
from ldapadapter.exceptions import NoSuchObject

class FakeLDAPAdapter:
    implements(ILDAPAdapter)
    _isDown = False
    def connect(self, dn=None, password=None):
        if self._isDown:
            raise ServerDown
        if not dn and not password:
            return FakeLDAPConnection()
        if dn == 'uid=42,dc=test' and password == '42pw':
            return FakeLDAPConnection()
        raise InvalidCredentials

class FakeLDAPConnection:
    def search(self, base, scope='sub', filter='(objectClass=*)', attrs=[]):
        dn1 = u'uid=1,dc=test'
        entry1 = {'cn': [u'many'],
                  'uid': [u'1'],
                  'sn': [u'mr1'],
                  }
        dn2 = u'uid=2,dc=test'
        entry2 = {'cn': [u'many'],
                  'uid': [u'2'],
                  'sn': [u'mr2'],
                  }
        dn42 = u'uid=42,dc=test'
        entry42 = {'cn': [u'ok'],
                   'uid': [u'42'],
                   'sn': [u'the question'],
                   'mult': [u'm1', u'm2'],
                   }
        if base.endswith('dc=bzzt'):
            raise NoSuchObject
        if filter == '(cn=none)':
            return []
        if filter in ('(cn=many)', '(cn=*many*)'):
            return [(dn1, entry1), (dn2, entry2)]
        if filter == '(cn=ok)' or filter == '(uid=42)':
            return [(dn42, entry42)]
        if filter in ('(&(sn=*mr2*)(cn=*many*))', '(&(cn=*many*)(sn=*mr2*))'):
            return [(dn2, entry2)]
        if filter == '(objectClass=*)':
            return [(dn1, entry1), (dn2, entry2), (dn42, entry42)]
        return []

def setUp(test):
    root = setup.placefulSetUp(site=True)
    sm = zapi.getServices(root)
    setup.addService(sm, Utilities, LocalUtilityService())
    setup.addUtility(sm, 'fake_ldap_adapter', ILDAPAdapter,
                     FakeLDAPAdapter())

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('ldappas.authentication',
                             setUp=setUp, tearDown=tearDown,
                             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

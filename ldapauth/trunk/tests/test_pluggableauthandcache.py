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

$Id$
"""

import sys
from unittest import TestCase, TestSuite, makeSuite, main

# FakeLDAP taken from LDAPUserFolder of Jens Vagelpohl
import FakeLDAP
if sys.modules.has_key('_ldap'):
    del sys.modules['_ldap']
sys.modules['ldap'] = FakeLDAP

import ldap

from zope.interface import implements, classImplements

from zope.app import zapi
from zope.app.tests import ztapi, setup
from zope.app.site.tests import placefulsetup

from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.annotation.attribute import AttributeAnnotations

from zope.app.cache.interfaces import ICacheable, ICache
from zope.app.cache.annotationcacheable import AnnotationCacheable
from zope.app.cache.caching import getCacheForObject

from zope.app.pluggableauth import PluggableAuthenticationService, \
        SimplePrincipal

from ldapauth.source import LDAPPrincipalSource
from zope.exceptions import NotFoundError

# Cachin test idea shamefully taken from
# zope.app.sqlscript.tests.test_sqlscript
class CacheStub:
    implements(ICache)
    def __init__(self):
        self.cache = {}

    def set(self, data, obj, key=None):
        if key:
            keywords = key.items()
            keywords.sort()
            keywords = tuple(keywords)
        self.cache[obj, keywords] = data

    def query(self, obj, key=None, default=None):
        if key:
            keywords = key.items()
            keywords.sort()
            keywords = tuple(keywords)
        return self.cache.get((obj, keywords), default)


class PluggableAuthAndCacheTest(placefulsetup.PlacefulSetup, TestCase):
    
    def setUp(self):
        classImplements(LDAPPrincipalSource, IAttributeAnnotatable)
        self.createUsersAndLDAP()

        sm = placefulsetup.PlacefulSetup.setUp(self, site=True)

        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                AttributeAnnotations)
        ztapi.provideAdapter(IAnnotatable, ICacheable, AnnotationCacheable)
        
        auth = setup.addService(sm, 'PluggableAuthenticationService',
                PluggableAuthenticationService())
        self._auth = auth
        source = LDAPPrincipalSource(
                'localhost', 389, 'ou=people,dc=fake',
                'uid', 'cn=Manager,dc=fake', 'root')
        self._source = source
        auth.addPrincipalSource('ldap', source)

    def createUsersAndLDAP(self):
        l = ldap.initialize('ldap://localhost:389')
        l.simple_bind_s('cn=Manager,dc=fake', 'root')
        self._toto = SimplePrincipal('toto_l', 'toto_p')
        self._tata = SimplePrincipal('tata_l', 'tata_p')
        self._titi = SimplePrincipal('titi_l', 'titi_p')
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

    def test_authServiceGetPrincipal(self):
        auth = self._auth
        source = self._source
        source_toto = source.getPrincipal('\t\ttoto_l')
        auth_toto = auth.getPrincipal(source_toto.id)
        self.assertEqual('toto_l', auth_toto.login)
        self.assertEqual('toto_p', auth_toto.password)

    def test_authServiceGetPrincipals(self):
        users = self._auth.getPrincipals('t')
        self.assertEquals(len(list(users)), 3)
        for user in users:
            self.assert_('t' in user.login)
        self.assertEquals(len(list(self._auth.getPrincipals('ta'))), 1)

    def test_authServiceAuthenticate(self):
        pass

    def test_cache(self):
        auth = self._auth
        source = self._source
        toto = source.getPrincipal('\t\ttoto_l')
        self.assertNotEqual(auth.getPrincipal(toto.id),
                auth.getPrincipal(toto.id))
        AnnotationCacheable(source).setCacheId('dumbcache')
        ztapi.provideUtility(ICache, CacheStub(), 'dumbcache')
        self.assertEqual(auth.getPrincipal(toto.id),
                auth.getPrincipal(toto.id))

def test_suite():
    return TestSuite((
        makeSuite(PluggableAuthAndCacheTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

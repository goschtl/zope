##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_configurationregistry.py,v 1.4 2003/03/23 22:35:42 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.proxy.context import ContextWrapper, getItem
from zope.app.services.configuration import ConfigurationRegistry
from zope.app.services.service import ServiceManager
from zope.app.traversing import traverse

class Configuration:

    active = 0

    def activated(self):
        self.active += 1

    def deactivated(self):
        self.active -= 1


class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        root = self.rootFolder

        root.setServiceManager(ServiceManager())
        self.__default = traverse(root, "++etc++site/default")
        self.__registry = ContextWrapper(ConfigurationRegistry(), root)

    def __config(self, name):
        self.__default.setObject(name, Configuration())
        return getItem(self.__default, name)

    def test_register_and_registered_and_nonzero_and_active(self):
        registry = self.__registry

        self.assertEqual(registry.active(), None)

        self.failIf(registry)
        self.__c1 = c1 = self.__config("1")
        registry.register(c1)
        self.failUnless(registry)
        self.failUnless(registry.registered(c1))
        self.assertEqual(c1.active, 0)

        self.assertEqual(registry.active(), None)

        self.__c2 = c2 = self.__config("2")
        self.failIf(registry.registered(c2))
        registry.register(c2)
        self.failUnless(registry)
        self.failUnless(registry.registered(c2))
        self.assertEqual(c2.active, 0)


    def test_unregister_and_registered_and_nonzero(self):
        # reuse registration test to set things up (more)
        self.test_register_and_registered_and_nonzero_and_active()

        registry = self.__registry

        c1 = self.__c1
        registry.unregister(c1)
        self.failIf(registry.registered(c1))
        self.assertEqual(c1.active, 0)

        c2 = self.__c2
        registry.unregister(c2)
        self.failIf(registry.registered(c2))
        self.assertEqual(c2.active, 0)

        self.failIf(registry)

    def test_activate_and_active(self):
        # reuse registration test to set things up (more)
        self.test_register_and_registered_and_nonzero_and_active()

        registry = self.__registry
        self.assertEqual(registry.active(), None)

        c1 = self.__c1
        c2 = self.__c2

        registry.activate(c2)
        self.assertEqual(c1.active, 0)
        self.failUnless(registry.registered(c1))
        self.assertEqual(c2.active, 1)
        self.failUnless(registry.registered(c2))
        self.assertEqual(registry.active(), c2)

        registry.activate(c2)
        self.assertEqual(c1.active, 0)
        self.failUnless(registry.registered(c1))
        self.assertEqual(c2.active, 1)
        self.failUnless(registry.registered(c2))
        self.assertEqual(registry.active(), c2)

        registry.activate(c1)
        self.assertEqual(c1.active, 1)
        self.failUnless(registry.registered(c1))
        self.assertEqual(c2.active, 0)
        self.failUnless(registry.registered(c2))
        self.assertEqual(registry.active(), c1)

    def test_activate_unregistered(self):
        registry = self.__registry
        self.assertRaises(ValueError, registry.activate, self.__config('3'))
        self.test_activate_and_active()
        self.assertRaises(ValueError, registry.activate, self.__config('4'))

    def test_deactivate(self):
        self.test_activate_and_active()

        registry = self.__registry
        c1 = self.__c1
        c2 = self.__c2
        self.assertEqual(registry.active(), c1)

        registry.deactivate(c2)
        self.assertEqual(c2.active, 0)
        self.assertEqual(registry.active(), c1)

        registry.deactivate(c1)
        self.assertEqual(c2.active, 0)
        self.assertEqual(c1.active, 0)
        self.assertEqual(registry.active(), None)

        self.failUnless(registry.registered(c1))
        self.failUnless(registry.registered(c2))

    def test_unregister_active(self):
        self.test_activate_and_active()

        registry = self.__registry
        c1 = self.__c1
        c2 = self.__c2
        self.assertEqual(registry.active(), c1)

        registry.unregister(c1)
        self.assertEqual(c2.active, 0)
        self.assertEqual(c1.active, 0)
        self.assertEqual(registry.active(), None)

        self.failIf(registry.registered(c1))
        self.failUnless(registry.registered(c2))

    def test_deactivate_unregistered(self):
        registry = self.__registry
        self.assertRaises(ValueError, registry.deactivate, self.__config('3'))

    def test_info(self):
        self.test_activate_and_active()

        registry = self.__registry
        c1 = self.__c1
        c2 = self.__c2

        info = registry.info()
        info.sort(lambda a, b: cmp(a['id'], b['id']))
        self.assertEqual(
            info,
            [
              {'id': 'default/1',
               'active': True,
               'configuration': c1,
               },
              {'id': 'default/2',
               'active': False,
               'configuration': c2,
               },
              ])

        registry.deactivate(c1)

        info = registry.info()
        info.sort(lambda a, b: cmp(a['id'], b['id']))
        self.assertEqual(
            info,
            [
              {'id': 'default/1',
               'active': False,
               'configuration': c1,
               },
              {'id': 'default/2',
               'active': False,
               'configuration': c2,
               },
              ])

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

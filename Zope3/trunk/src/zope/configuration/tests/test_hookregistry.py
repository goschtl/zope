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
"""

$Id: test_hookregistry.py,v 1.3 2003/05/01 19:35:40 faassen Exp $
"""

import unittest

def dummyHook():
    return "hooked implementation"

class HookRegistryTest(unittest.TestCase):

    def testAddHookable(self):
        from zope.configuration.hookregistry import HookRegistry

        hookableAddr = (
            'zope.configuration.tests.hooktestdummymodule.dummyHookable')

        hookRegistry=HookRegistry()
        hookRegistry.addHookable(hookableAddr)
        hookables=hookRegistry.getHookables()
        self.assertEquals(len(hookables), 1)
        self.assertEquals(hookables[0][0], hookableAddr)
        self.assertEquals(hookables[0][1],0)

    def testAddDuplicateHookable(self):
        from zope.configuration.hookregistry import HookRegistry
        from zope.exceptions import DuplicationError

        hookableAddr = (
            'zope.configuration.tests.hooktestdummymodule.dummyHookable')
        hookRegistry=HookRegistry()
        hookRegistry.addHookable(hookableAddr)
        self.assertRaises(DuplicationError, hookRegistry.addHookable,
                          hookableAddr)

    def testAddInvalidHookable(self):
        from zope.configuration.hookregistry import HookRegistry, \
             BadHookableError
        hookRegistry=HookRegistry()
        self.assertRaises(BadHookableError, hookRegistry.addHookable,
                          'foo.bar.this.should.not.resolve.anywhere')
        self.assertRaises(BadHookableError, hookRegistry.addHookable,
                          'zope')
        self.assertRaises(
            BadHookableError, hookRegistry.addHookable,
            'zope.configuration.hookregistry.hookregistry.addHookable')

    def testAddHook(self):
        from zope.configuration.hookregistry import \
             HookRegistry, BadHookError, DuplicateHookError, \
             MissingHookableError
        from zope.configuration.tests.hooktestdummymodule \
             import associatedDummy

        dummyHook = 'zope.configuration.tests.test_hookregistry.dummyHook'
        suite = 'zope.configuration.tests.test_hookregistry.test_suite'
        hookableParent = 'zope.configuration.tests.hooktestdummymodule'
        hookableLast = 'dummyHookable'
        hookableAddr = '%s.%s' % (hookableParent, hookableLast)
        old = __import__(hookableParent, {}, {}, ('__dict__',)) # for cleanup
        old = getattr(old, hookableLast)
        self.assertEquals(old(), "original implementation")

        hookRegistry = HookRegistry()
        hookRegistry.addHookable(hookableAddr)
        self.assertRaises(BadHookError, hookRegistry.addHook, hookableAddr,
                          'foo.bar.this.should.not.resolve.anywhere')
        hookRegistry.addHook(hookableAddr, dummyHook)
        new = __import__(hookableParent, {}, {}, ('__dict__',))
        new = getattr(new, hookableLast)
        self.assertEquals(new(), "hooked implementation")
        self.assertEquals(associatedDummy(), "hooked implementation")
        from zope.configuration.tests.hooktestdummymodule \
             import associatedDummy as associatedDummyAgain
        self.assertEquals(associatedDummyAgain(), "hooked implementation")
        self.assertRaises(DuplicateHookError, hookRegistry.addHook,
                          hookableAddr, suite)
        self.assertRaises(MissingHookableError, hookRegistry.addHook,
                          suite, dummyHook)
        setattr(__import__(hookableParent, {}, {}, ('__dict__',)),
                hookableLast, old) # cleanup

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(HookRegistryTest)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

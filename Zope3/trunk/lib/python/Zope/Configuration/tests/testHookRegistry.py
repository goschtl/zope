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

$Id: testHookRegistry.py,v 1.3 2002/07/11 22:42:33 jeremy Exp $
"""

import unittest, sys

def dummyHook():
    return "hooked implementation"

class HookRegistryTest(unittest.TestCase):

#    def setUp(self):
#
#        from Zope.Configuration.tests import Products_
#        self.old=sys.modules.get('ZopeProducts', None)
#        sys.modules['ZopeProducts']=Products_
#
#    def tearDown(self):
#        old=self.old
#        if old is None: del sys.modules['ZopeProducts']
#        else: sys.modules['ZopeProducts']=self.old
        
    def testAddHookable(self):
        from Zope.Configuration.HookRegistry import HookRegistry
        
        hookableAddr='Zope.Configuration.tests.hookTestDummyModule.dummyHookable'
        
        hookRegistry=HookRegistry()
        hookRegistry.addHookable(hookableAddr)
        hookables=hookRegistry.getHookables()
        self.assertEquals(len(hookables), 1)
        self.assertEquals(hookables[0][0], hookableAddr)
        self.assertEquals(hookables[0][1],0)
    
    def testAddDuplicateHookable(self):
        from Zope.Configuration.HookRegistry import HookRegistry
        from Zope.Exceptions import DuplicationError
        
        hookableAddr='Zope.Configuration.tests.hookTestDummyModule.dummyHookable'
        hookRegistry=HookRegistry()
        hookRegistry.addHookable(hookableAddr)
        self.assertRaises(DuplicationError, hookRegistry.addHookable,
                          hookableAddr)
        
    def testAddInvalidHookable(self):
        from Zope.Configuration.HookRegistry import HookRegistry, \
             BadHookableError
        hookRegistry=HookRegistry()
        self.assertRaises(BadHookableError, hookRegistry.addHookable,
                          'foo.bar.this.should.not.resolve.anywhere')
        self.assertRaises(BadHookableError, hookRegistry.addHookable,
                          'Zope')
        self.assertRaises(BadHookableError, hookRegistry.addHookable,
                          'Zope.Configuration.HookRegistry.HookRegistry.addHookable')
        
    def testAddHook(self):
        from Zope.Configuration.HookRegistry import \
             HookRegistry, BadHookError, DuplicateHookError, \
             MissingHookableError
        from Zope.Configuration.tests.hookTestDummyModule \
             import associatedDummy

        dummyHook = 'Zope.Configuration.tests.testHookRegistry.dummyHook'
        suite = 'Zope.Configuration.tests.testHookRegistry.test_suite'
        hookableParent = 'Zope.Configuration.tests.hookTestDummyModule'
        hookableLast = 'dummyHookable'
        hookableAddr = '%s.%s' % (hookableParent, hookableLast)
        old = __import__(hookableParent, {}, {}, ('__dict__',)) # for cleanup
        old = getattr(old, hookableLast)
        self.assertEquals(old(), "original implementation")
        
        hookRegistry = HookRegistry()
        hookRegistry.addHookable(hookableAddr)
        self.assertRaises(BadHookError, hookRegistry.addHook,
                          hookableAddr,
                          'foo.bar.this.should.not.resolve.anywhere')
        hookRegistry.addHook(hookableAddr, dummyHook)
        new = __import__(hookableParent, {}, {}, ('__dict__',))
        new = getattr(new, hookableLast)
        self.assertEquals(new(), "hooked implementation")
        self.assertEquals(associatedDummy(), "hooked implementation")
        from Zope.Configuration.tests.hookTestDummyModule \
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

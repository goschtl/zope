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
"""Unit tests for SecurityManager

$Id: test_manager.py,v 1.5 2004/03/13 17:21:51 philikon Exp $
"""

import unittest

from zope.interface.verify import verifyClass

from zope.security import manager
from zope.security.simplepolicies import ParanoidSecurityPolicy
from zope.security.simplepolicies import PermissiveSecurityPolicy
from zope.security.context import SecurityContext

class DummyExecutable:
    """implements( (pseudo) IExecutableObject)"""

class DummyExecutableWithCustomPolicy:
    """implements( (pseudo) IExecutableObjectWithCustomSecurityPolicy)"""

    def _customSecurityPolicy(self):
        return PermissiveSecurityPolicy()

class Test(unittest.TestCase):

    def setUp(self):
        self._oldPolicy = manager._defaultPolicy
        manager.setSecurityPolicy(ParanoidSecurityPolicy())
        self._context = SecurityContext('xyzzy')

    def tearDown(self):
        from zope.security.manager import setSecurityPolicy
        setSecurityPolicy(self._oldPolicy)

    def _makeMgr(self):
        from zope.security.manager import SecurityManager
        return SecurityManager(self._context)

    def _setPermissive(self):
        from zope.security.manager import setSecurityPolicy
        setSecurityPolicy(PermissiveSecurityPolicy())


    def test_import(self):
        from zope.security.manager import SecurityManager
        from zope.security.interfaces import ISecurityManager
        verifyClass(ISecurityManager, SecurityManager)

    def test_empty(self):
        mgr = self._makeMgr()
        self.assertEqual(mgr.getPrincipal(), self._context.user)
        self.failIf(mgr.calledByExecutable())

    def test_w_default_policy(self):
        mgr = self._makeMgr()
        self.failIf(mgr.checkPermission(None, None))

    def test_w_permissive_policy(self):
        mgr = self._makeMgr()
        self._setPermissive()
        self.failUnless(mgr.checkPermission(None, None))

    def test_exec_stack_overflow(self):
        from zope.security.manager import MAX_STACK_SIZE
        mgr = self._makeMgr()

        for i in range(MAX_STACK_SIZE):
            mgr.pushExecutable(None)

        self.assertRaises(SystemError, mgr.pushExecutable, None)

    def test_pushExecutable_simple(self):
        mgr = self._makeMgr()
        self.failIf(mgr.calledByExecutable())

        mgr.pushExecutable(DummyExecutable())
        self.failUnless(mgr.calledByExecutable())

    def test_popExecutable_simple(self):
        mgr = self._makeMgr()
        exe = DummyExecutable()
        exe2 = DummyExecutable()

        mgr.pushExecutable(exe)
        mgr.pushExecutable(exe2)
        mgr.popExecutable(exe2)
        self.failUnless(mgr.calledByExecutable())

        mgr.popExecutable(exe)
        self.failIf(mgr.calledByExecutable())

    def test_popExecutable_nomatch(self):
        mgr = self._makeMgr()
        exe = DummyExecutable()
        exe2 = DummyExecutable()
        other = DummyExecutable()

        mgr.pushExecutable(exe)
        mgr.pushExecutable(exe2)
        mgr.popExecutable(other) # not on stack => no change
        self.failUnless(mgr.calledByExecutable())

        mgr.popExecutable(exe) # bottom of stack => empty it
        self.failIf(mgr.calledByExecutable())

    def test_pushExecutable_customPolicy(self):
        mgr = self._makeMgr()
        exe = DummyExecutableWithCustomPolicy()
        self.failIf(mgr.checkPermission(None, None))
        mgr.pushExecutable(exe)
        self.failUnless(mgr.checkPermission(None, None))
        mgr.popExecutable(exe)
        self.failIf(mgr.checkPermission(None, None))

    def test_pushPop_complexPolicies(self):
        mgr = self._makeMgr()

        exe1 = DummyExecutableWithCustomPolicy()
        exe2 = DummyExecutable()
        exe3 = DummyExecutableWithCustomPolicy()

        mgr.pushExecutable(exe1) # now has custom permissive policy
        self.failUnless(mgr.checkPermission(None, None))

        mgr.pushExecutable(exe2) # now has default policy
        self.failIf(mgr.checkPermission(None, None))

        mgr.pushExecutable(exe3) # now has custom permissive policy
        self.failUnless(mgr.checkPermission(None, None))

        mgr.popExecutable(exe3) # back to default policy
        self.failIf(mgr.checkPermission(None, None))

        mgr.popExecutable(exe2) # back to has custom permissive policy
        self.failUnless(mgr.checkPermission(None, None))

        mgr.popExecutable(exe1) # back to default policy
        self.failIf(mgr.checkPermission(None, None))


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

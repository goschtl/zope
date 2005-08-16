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
""" Unit tests for SecurityManagement

$Id$
"""

import unittest

from zope.interface.verify import verifyObject
from zope.testing.cleanup import CleanUp


class Test(CleanUp, unittest.TestCase):

    def test_import(self):
        from zope.security import management
        from zope.security.interfaces import ISecurityManagement
        from zope.security.interfaces import IInteractionManagement

        verifyObject(ISecurityManagement, management)
        verifyObject(IInteractionManagement, management)

    def test_securityPolicy(self):
        from zope.security.management import setSecurityPolicy
        from zope.security.management import getSecurityPolicy
        from zope.security.simplepolicies import PermissiveSecurityPolicy

        policy = PermissiveSecurityPolicy()
        setSecurityPolicy(policy)
        self.assert_(getSecurityPolicy() is policy)

    def test_queryInteraction(self):
        # XXX this test is a bit obfuscated
        from zope.security.management import queryInteraction

        marker = object()
        class ThreadVars:
            interaction = marker
        class ThreadStub:
            __zope3_thread_globals__ = ThreadVars()

        self.assert_(queryInteraction(_thread=ThreadStub()) is marker)

    def test_newInteraction(self):
        # XXX this test is a bit obfuscated
        from zope.security.management import newInteraction

        class ThreadVars:
            interaction = None
        class ThreadStub:
            __zope3_thread_globals__ = ThreadVars()

        rq = None
        thread = ThreadStub()
        newInteraction(rq, _thread=thread)
        self.assert_(thread.__zope3_thread_globals__.interaction is not None)

        self.assertRaises(AssertionError, newInteraction, rq, _thread=thread)

    def test_endInteraction(self):
        # XXX this test is a bit obfuscated
        from zope.security.management import endInteraction

        marker = object()
        class ThreadVars:
            interaction = marker
        class ThreadStub:
            __zope3_thread_globals__ = ThreadVars()

        thread = ThreadStub()
        endInteraction(_thread=thread)
        self.assert_(thread.__zope3_thread_globals__.interaction is None)

        # again
        endInteraction(_thread=thread)
        self.assert_(thread.__zope3_thread_globals__.interaction is None)

    def test_checkPermission(self):
        from zope.security import checkPermission
        from zope.security.management import setSecurityPolicy
        from zope.security.management import queryInteraction
        from zope.security.management import newInteraction

        permission = 'zope.Test'
        obj = object()
        interaction = object()

        class InteractionStub:
            pass

        class PolicyStub:
            def createInteraction(s, r):
                return InteractionStub()

            def checkPermission(s, p, o, i):
                self.assert_(p is permission)
                self.assert_(o is obj)
                self.assert_(i is queryInteraction() or i is interaction)
                return i is interaction

        setSecurityPolicy(PolicyStub())
        newInteraction(None)
        self.assertEquals(checkPermission(permission, obj), False)
        self.assertEquals(checkPermission(permission, obj, interaction), True)


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

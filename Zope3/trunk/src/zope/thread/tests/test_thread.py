##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Unit tests for zope.thread.

$Id$
"""

import unittest
from zope.interface.verify import verifyObject


class ThreadStub:
    pass


class TestThread(unittest.TestCase):

    def test_ThreadGlobals(self):
        from zope.thread import ThreadGlobals
        from zope.thread.interfaces import IInteractionThreadGlobal
        from zope.thread.interfaces import ISiteThreadGlobal
        globals = ThreadGlobals()
        verifyObject(IInteractionThreadGlobal, globals)
        verifyObject(ISiteThreadGlobal, globals)

    def test_thread_globals(self):
        from zope.thread import thread_globals
        from zope.thread.interfaces import IInteractionThreadGlobal
        fake_thread = ThreadStub()
        another_thread = ThreadStub()
        globals = thread_globals(fake_thread)
        verifyObject(IInteractionThreadGlobal, globals)
        self.assert_(thread_globals(fake_thread) is globals)
        self.assert_(thread_globals(another_thread) is not globals)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestThread))
    return suite


if __name__ == '__main__':
    unittest.main()


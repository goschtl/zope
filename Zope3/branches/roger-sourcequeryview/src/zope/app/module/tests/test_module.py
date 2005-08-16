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
"""Peristent Module tests

$Id$
"""
import unittest

from zope.interface import Interface, implements
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.traversing.api import traverse
from zope.app.module import Manager
from ZODB.tests.util import DB
from transaction import get_transaction


class ITestService(Interface):
    pass

class TestService(object):

    implements(ITestService)


NAME = 'zope.app.module.tests.sample1'

called = 0

SOURCE = """\
class C(object):
    def __init__(self, v):
        self.ini = v

x = 1
from zope.app.module.tests import test_module

test_module.called += 1
"""

class LocalModuleTests(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)
        self.sm = traverse(self.rootFolder, "++etc++site")
        default = traverse(self.sm, "default")
        old_called = called
        default[NAME] = Manager(NAME, SOURCE)
        self.manager = traverse(default, NAME)
        self.assertEqual(called, old_called)
        self.manager.execute()
        self.assertEqual(called, old_called + 1)

    def test_module_persistence(self):
        db = DB()
        conn = db.open()
        root = conn.root()
        root['Application'] = self.rootFolder
        get_transaction().commit()
        # The findModule() here is only for the
        # RegisterableContainer, not the SiteManager.
        default = traverse(self.rootFolder, "++etc++site/default")
        m = default.findModule(NAME)

        c = m.C(42)
        self.assertEqual(c.ini, 42)
        self.assertEqual(m.x, 1)

        # This tests that the module can be seen from a different
        # connection; an earlier version had a bug that requires this
        # regression check.
        conn2 = db.open()
        rootFolder2 = conn2.root()['Application']
        default = traverse(rootFolder2, "++etc++site/default")
        m = default.findModule(NAME)

        c = m.C(42)
        self.assertEqual(c.ini, 42)
        self.assertEqual(m.x, 1)

    def test_recompile(self):
        old_called = called
        self.manager.source += "\n"
        self.assertEqual(called, old_called)
        m = self.manager.getModule()
        self.assertEqual(called, old_called+1)
        m = self.manager.getModule()
        self.assertEqual(called, old_called+1)
        


def test_suite():
    return unittest.makeSuite(LocalModuleTests)

if __name__=='__main__':
    unittest.main(defaultTest="test_suite")

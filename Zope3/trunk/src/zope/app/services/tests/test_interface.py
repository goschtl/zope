##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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

import unittest

from transaction import get_transaction

from zodb.storage.mapping import DB
from zodb.code.module import ManagedRegistry

from zope.app.services.interface import PersistentInterface

code = """\
from zope.interface import Interface

class IFoo(Interface):
    pass

class Foo:
    __implements__ = IFoo

aFoo = Foo()
"""

class PersistentInterfaceTest(unittest.TestCase):

    def setUp(self):
        self.db = DB()
        self.root = self.db.open().root()
        self.registry = ManagedRegistry()
        self.root["registry"] = self.registry
        get_transaction().commit()

    def tearDown(self):
        get_transaction().abort() # just in case
    
    def test_creation(self):
        class IFoo(PersistentInterface):
            pass

        class Foo:
            __implements__ = IFoo

        self.assert_(IFoo.isImplementedBy(Foo()))
        self.assertEqual(IFoo._p_oid, None)

    def test_patch(self):
        self.registry.newModule("imodule", code)
        get_transaction().commit()
        imodule = self.registry.findModule("imodule")
        print imodule.aFoo
        print imodule.aFoo.__implements__
        print imodule.IFoo
        print imodule.IFoo.isImplementedBy(imodule.aFoo)
        self.assert_(imodule.IFoo.isImplementedBy(imodule.aFoo))
        

def test_suite():
    return unittest.makeSuite(PersistentInterfaceTest)

##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Interface implementation tests

$Id$
"""

import os
import unittest
from types import ListType, TupleType

from Interface import Interface
from Interface.IInterface import IInterface
from Interface.Verify import verifyClass


class InterfaceImplChecker:

    def _test_object_imp(self, c):
        try:
            impl = c.__implements__
            self._verify(impl, c)
        except:
            print '%s incorrectly implements %s' % (repr(c), repr(impl))
            raise

    def _test_all_in_module(self, m):
        name = m.__name__
        for attr, value in m.__dict__.items():
            if (hasattr(value, '__implements__') and
                not IInterface.isImplementedBy(value)
                and getattr(value, '__module__', None) == name):
                self._test_object_imp(value)

    def _test_all_in_package(self, p):
        seen = {'__init__': 1}
        for path in p.__path__:
            names = os.listdir(path)
            for name in names:
                base, ext = os.path.splitext(name)
                ext = ext.lower()
                if ext in ('.py', '.pyc', '.pyo'):
                    if seen.has_key(base):
                        continue
                    seen[base] = 1
                    modname = '%s.%s' % (p.__name__, base)
                    m = __import__(modname, {}, {}, ('__doc__',))
                    self._test_all_in_module(m)

    def _verify(self, iface, c):
        if isinstance(iface, ListType) or isinstance(iface, TupleType):
            for item in iface:
                self._verify(item, c)
        else:
            verifyClass(iface, c)
            for base in iface.getBases():
                self._verify(base, c)

    
class ApelibImplTests(InterfaceImplChecker, unittest.TestCase):

    def test_core_implementations(self):
        import apelib.core
        self._test_all_in_package(apelib.core)

    def test_zope2_implementations(self):
        import apelib.zope2
        self._test_all_in_package(apelib.zope2)

    def test_fs_implementations(self):
        import apelib.fs
        self._test_all_in_package(apelib.fs)

    def test_zodb3_implementations(self):
        import apelib.zodb3
        self._test_all_in_package(apelib.zodb3)

if __name__ == '__main__':
    unittest.main()


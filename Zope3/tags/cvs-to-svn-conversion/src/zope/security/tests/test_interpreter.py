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

from zope.security.interpreter import RestrictedInterpreter
from zope.security.checker import defineChecker

from zope.testing.cleanup import CleanUp

class RITests(unittest.TestCase, CleanUp):

    def setUp(self):
        CleanUp.setUp(self)
        self.rinterp = RestrictedInterpreter()

    def tearDown(self):
        CleanUp.tearDown(self)

    def testExec(self):
        self.rinterp.ri_exec("str(type(1))\n")

    def testImport(self):
        self.rinterp.ri_exec("import zope.security.proxy")

    def testWrapping(self):
        # make sure we've really got proxies
        import types
        from zope.security.checker import NamesChecker

        checker = NamesChecker(['Proxy'])

        import zope.security.proxy
        defineChecker(zope.security.proxy, checker)

        checker = NamesChecker(['BuiltinFunctionType'])
        defineChecker(types, checker)

        code = ("from zope.security.proxy import Proxy\n"
                "import types\n"
                "assert type(id) is not types.BuiltinFunctionType\n"
                )
        self.rinterp.ri_exec(code)

    def testGlobalVersusLocal(self):
        code = ("global x\n"
                "x = 1\n"
                "y = 2\n")
        self.rinterp.ri_exec(code)
        self.assert_('x' in self.rinterp.globals)
        self.assert_('y' not in self.rinterp.globals)
        self.assertEqual(self.rinterp.globals['x'], 1)
        self.assert_('x' not in self.rinterp.locals)
        self.assert_('y' in self.rinterp.locals)
        self.assertEqual(self.rinterp.locals['y'], 2)


def test_suite():
    return unittest.makeSuite(RITests)


if __name__=='__main__':
    from unittest import main
    main(defaultTest='test_suite')

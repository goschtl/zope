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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

Revision information:
$Id: test_restrictedbuiltins.py,v 1.2 2002/12/25 14:15:22 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.testing.cleanup import CleanUp # Base class w registry cleanup

class Test(CleanUp, TestCase):

    def test(self):
        from zope.security.restrictedbuiltins import RestrictedBuiltins
        from zope.security.proxy import Proxy
        from zope.exceptions import Forbidden

        def e(expr):
            return eval(expr, {'__builtins__': RestrictedBuiltins})

        self.assertEqual(e('__import__("sys").__name__'), "sys")
        self.assertEqual(e('__import__("zope.security").__name__'), "zope")
        self.assertEqual(e(
            '__import__("zope.security", {}, None, ["__doc__"]).__name__'),
                         "zope.security")
        self.assertRaises(Forbidden, e, '__import__("sys").exit')



def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')

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
$Id: testRestrictedBuiltins.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

class Test(CleanUp, TestCase):

    def test(self):
        from Zope.Security.RestrictedBuiltins import RestrictedBuiltins
        from Zope.Security.Proxy import Proxy
        from Zope.Exceptions import Forbidden

        def e(expr):
            return eval(expr, {'__builtins__': RestrictedBuiltins})

        self.assertEqual(e('__import__("sys").__name__'), "sys")
        self.assertEqual(e('__import__("Zope.Security").__name__'), "Zope")
        self.assertEqual(e(
            '__import__("Zope.Security",{},None,("__doc__",)).__name__'),
                         "Zope.Security")
        self.assertRaises(Forbidden, e, '__import__("sys").exit')
        
    

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

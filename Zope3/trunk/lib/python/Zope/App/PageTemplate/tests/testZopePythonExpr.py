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
$Id: testZopePythonExpr.py,v 1.2 2002/06/10 23:28:14 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

class Engine:

    def getTypes(self):
        return {}

class Context:

    _engine = Engine()

    def __init__(self, **kw):
        self.vars = kw

class Test(CleanUp, TestCase):

      def test(self):
          from Zope.App.PageTemplate.Engine import ZopePythonExpr
          from Zope.Exceptions import Forbidden

          expr = ZopePythonExpr('python', 'max(a,b)', Engine())
          self.assertEqual(expr(Context(a=1, b=2)), 2)
          expr = ZopePythonExpr(
              'python', '__import__("sys").__name__', Engine())
          self.assertEqual(expr(Context()), 'sys')
          expr = ZopePythonExpr('python', '__import__("sys").exit',
                                Engine())
          self.assertRaises(Forbidden, expr, Context())
          expr = ZopePythonExpr('python', 'open("x", "w")', Engine())
          self.assertRaises(NameError, expr, Context())

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

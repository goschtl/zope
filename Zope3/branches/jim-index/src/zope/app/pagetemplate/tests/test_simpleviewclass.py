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
"""Simple View Class Tests

$Id$
"""
import unittest

class data: pass

class SimpleViewTestCase(unittest.TestCase):

    def test_simple(self):
        from zope.app.pagetemplate.tests.simpletestview import SimpleTestView

        ob = data()
        view = SimpleTestView(ob, None)
        macro = view['test']
        out = view()
        self.assertEqual(out,
                         '<html>\n'
                         '  <body>\n'
                         '    <p>hello world</p>\n'
                         '  </body>\n</html>\n')

    def test_WBases(self):
        from zope.app.pagetemplate.simpleviewclass import SimpleViewClass

        class C: pass

        SimpleTestView = SimpleViewClass('testsimpleviewclass.pt', bases=(C, ))

        self.failUnless(issubclass(SimpleTestView, C))

        ob = data()
        view = SimpleTestView(ob, None)
        macro = view['test']
        out = view()
        self.assertEqual(out,
                         '<html>\n'
                         '  <body>\n'
                         '    <p>hello world</p>\n'
                         '  </body>\n</html>\n')

def test_suite():
    return unittest.makeSuite(SimpleViewTestCase)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

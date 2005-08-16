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
"""Bound Page Template Tests

$Id$
"""
import unittest

class Test(unittest.TestCase):

    def testAttributes(self):

        from zope.app.pagetemplate.tests.sample import C

        self.assertRaises(AttributeError, setattr, C.index, 'foo', 1)
        self.assertRaises(AttributeError, setattr, C().index, 'foo', 1)

        C.index.im_func.foo = 1
        self.assertEqual(C.index.foo, 1)



def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: test_containmentiterator.py,v 1.3 2003/05/01 19:35:45 faassen Exp $
"""

import unittest

from zope.proxy.context import Wrapper, getbaseobject
from zope.proxy.context.containmentiterator import ContainmentIterator

class Test(unittest.TestCase):

    def  testWrapped(self):
        ob1 = 1
        ob2 = 2
        ob3 = 3
        ob4 = 4

        ob = Wrapper(Wrapper(ob3, Wrapper(ob2, ob1)), ob4)
        self.assertEqual(map(getbaseobject, ContainmentIterator(ob)),
                        [ 3, 2, 1 ])

    def  testUnWrapped(self):
        self.assertEqual(map(getbaseobject, ContainmentIterator(9)), [ 9 ])

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

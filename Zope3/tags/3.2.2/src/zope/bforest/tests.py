##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""test bforests

$Id$
"""

import unittest
from zope import bforest 
from zope.testing import doctest

def StringGenerator(src='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    "infinite-ish unique string generator"
    for el in src:
        yield el
    for pre in StringGenerator(src):
        for el in src:
            yield pre + el

def NumberGenerator(number=0, interval=1):
    "infinite-ish unique number generator"
    while 1:
        yield number
        number += interval

def test_suite():
    suite = unittest.TestSuite()
    numgen = iter(NumberGenerator()).next
    strgen = iter(StringGenerator()).next
    suite.addTest(
        doctest.DocFileSuite(
            'bforest.txt', 
            globs={'BForest': bforest.IOBForest, 
                   'KeyGenerator': numgen, 
                   'ValueGenerator': strgen}))
    suite.addTest(
        doctest.DocFileSuite(
            'bforest.txt', 
            globs={'BForest': bforest.OIBForest, 
                   'KeyGenerator': strgen, 
                   'ValueGenerator': numgen}))
    suite.addTest(
        doctest.DocFileSuite(
            'bforest.txt', 
            globs={'BForest': bforest.IIBForest, 
                   'KeyGenerator': numgen, 
                   'ValueGenerator': numgen}))
    suite.addTest(
        doctest.DocFileSuite(
            'bforest.txt', 
            globs={'BForest': bforest.OOBForest, 
                   'KeyGenerator': strgen, 
                   'ValueGenerator': strgen}))
    return suite

if __name__ == '__main__': 
    import unittest
    unittest.main(defaultTest='test_suite')

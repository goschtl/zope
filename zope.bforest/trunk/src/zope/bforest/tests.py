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

$Id: tests.py 29018 2005-02-02 15:28:36Z poster $
"""

import unittest
import datetime
from zope import bforest 
from zope.bforest import periodic
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

oldDatetime = datetime.datetime
class _datetime(oldDatetime):
    _now = None
    @classmethod
    def now(klass, tzinfo=None):
        if tzinfo is None:
            return klass._now.replace(tzinfo=None)
        else:
            return klass._now.astimezone(tzinfo)
    def astimezone(self, tzinfo):
        return _datetime(
            *super(_datetime,self).astimezone(tzinfo).__reduce__()[1])
    def replace(self, *args, **kwargs):
        return _datetime(
            *super(_datetime,self).replace(
                *args, **kwargs).__reduce__()[1])
    def __repr__(self):
        raw = super(_datetime, self).__repr__()
        return "datetime.datetime%s" % (
            raw[raw.index('('):],)
    def __reduce__(self):
        return (argh, super(_datetime, self).__reduce__()[1])
def setNow(dt):
    _datetime._now = _datetime(*dt.__reduce__()[1])
def argh(*args, **kwargs):
    return _datetime(*args, **kwargs)

def setUp(test):

    datetime.datetime = _datetime
    test.globs['setNow'] = setNow

def tearDown(test):
    datetime.datetime = oldDatetime # cleanup

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
    suite.addTest(
        doctest.DocFileSuite(
            'periodic.txt',
            globs={'BForest': periodic.IOBForest, 
                   'KeyGenerator': numgen, 
                   'ValueGenerator': strgen},
            setUp=setUp, tearDown=tearDown))
    suite.addTest(
        doctest.DocFileSuite(
            'periodic.txt', 
            globs={'BForest': periodic.OIBForest, 
                   'KeyGenerator': strgen, 
                   'ValueGenerator': numgen},
            setUp=setUp, tearDown=tearDown))
    suite.addTest(
        doctest.DocFileSuite(
            'periodic.txt', 
            globs={'BForest': periodic.IIBForest, 
                   'KeyGenerator': numgen, 
                   'ValueGenerator': numgen},
            setUp=setUp, tearDown=tearDown))
    suite.addTest(
        doctest.DocFileSuite(
            'periodic.txt', 
            globs={'BForest': periodic.OOBForest, 
                   'KeyGenerator': strgen, 
                   'ValueGenerator': strgen},
            setUp=setUp, tearDown=tearDown))
    return suite

if __name__ == '__main__': 
    import unittest
    unittest.main(defaultTest='test_suite')

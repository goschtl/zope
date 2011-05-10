##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
from zope.testing import setupstack

import doctest
import time
import unittest

_now = 1252400584.910615
def now():
    global _now
    _now += 1
    return _now
time_time = time.time

def setUp(test):
    setupstack.setUpDirectory(test)
    setupstack.register(test, setattr, time, 'time', time_time)
    time.time = now

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.test',
            setUp=setUp, tearDown=setupstack.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


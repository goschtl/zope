##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
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
import os
import unittest
import doctest
from zope.app.testing import setup
from zope.testing.doctestunit import DocFileSuite

import z3c.zalchemy.testing


def setUp(test):
    setup.placefulSetUp()
    z3c.zalchemy.testing.setUp(test)
    test.globs['dbTrFilename'] = 'z3c.zalchemy.test.transaction.db'
    test.globs['dbFilename'] = 'z3c.zalchemy.test1.db'
    test.globs['dbFilename2'] = 'z3c.zalchemy.test2.db'

def tearDown(test):
    z3c.zalchemy.testing.tearDown(test)
    try:
        os.remove(test.globs['dbTrFilename'])
    except:
        pass
    try:
        os.remove(test.globs['dbFilename'])
    except:
        pass
    try:
        os.remove(test.globs['dbFilename2'])
    except:
        pass
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('TRANSACTION.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('../README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


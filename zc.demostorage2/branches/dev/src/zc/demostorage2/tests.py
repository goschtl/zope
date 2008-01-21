##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
import unittest
import shutil
from ZODB.Transaction import get_transaction
from zope.testing import doctest

def cleanupReadme(test):
    get_transaction().abort()
    test.globs['db'].close()
    shutil.rmtree(test.globs['tempdir'])

def testSomeDlegation():
    r"""
    >>> class S:
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def registerDB(self, db, limit):
    ...         print self.name, db, limit
    ...     def close(self):
    ...         print self.name, 'closed'
    ...     getName = sortKey = getSize = __len__ = None
    ...     supportsUndo = undo = undoLog = undoInfo = None
    ...     supportsTransactionalUndo = None
    ...     def new_oid(self):
    ...         return '\0' * 8
    ...     def tpc_begin(self, t, tid, status):
    ...         print 'begin', tid, status
    ...     def tpc_abort(self, t):
    ...         pass

    >>> from demostorage2 import DemoStorage2
    >>> storage = DemoStorage2(S(1), S(2))

    >>> storage.registerDB(1, 2)
    1 1 2
    2 1 2

    >>> storage.close()
    1 closed
    2 closed

    >>> storage.tpc_begin(1, 2, 3)
    begin 2 3
    >>> storage.tpc_abort(1)

    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('synchronized.txt'),
        doctest.DocTestSuite(),
        doctest.DocFileSuite('README.txt', tearDown=cleanupReadme),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


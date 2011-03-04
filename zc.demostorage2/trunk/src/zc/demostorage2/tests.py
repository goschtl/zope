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
import time, unittest

from zope.testing import doctest
import zope.testing.setupstack

import transaction

def setUp(test):
    zope.testing.setupstack.setUpDirectory(test)
    zope.testing.setupstack.register(test, transaction.abort)

def testSomeDelegation():
    r"""
    >>> class S:
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def registerDB(self, db):
    ...         print self.name, db
    ...     def close(self):
    ...         print self.name, 'closed'
    ...     getName = sortKey = getSize = __len__ = history = getTid = None
    ...     isReadOnly = tpc_transaction = None
    ...     supportsUndo = undo = undoLog = undoInfo = None
    ...     supportsTransactionalUndo = None
    ...     def new_oid(self):
    ...         return '\0' * 8
    ...     def tpc_begin(self, t, tid, status):
    ...         print 'begin', tid, status
    ...     def tpc_abort(self, t):
    ...         pass

    >>> from zc.demostorage2 import DemoStorage2
    >>> storage = DemoStorage2(S(1), S(2))

    >>> storage.registerDB(1)
    1 1
    2 1

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
        doctest.DocTestSuite(
            setUp=setUp, tearDown=zope.testing.setupstack.tearDown,
            ),
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zope.testing.setupstack.tearDown,
            ),
        ))

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

Revision information:
$Id: test_zodbundomanager.py,v 1.3 2003/04/30 23:37:58 faassen Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.testing.cleanup import CleanUp # Base class w registry cleanup
from time import time

def dict(**kw): return kw

testdata = [
    dict(id='1', user_name='jim', time=time(), description='des 1'),
    dict(id='2', user_name='jim', time=time(), description='des 2'),
    dict(id='3', user_name='jim', time=time(), description='des 3'),
    dict(id='4', user_name='jim', time=time(), description='des 4'),
    dict(id='5', user_name='jim', time=time(), description='des 5'),
    dict(id='6', user_name='jim', time=time(), description='des 6'),
    dict(id='7', user_name='jim', time=time(), description='des 7'),
    ]
testdata.reverse()

class StubDB:

    def __init__(self):
        self.data = list(testdata)

    def undoInfo(self):
        return tuple(self.data)

    def undo(self, id):
        self.data = [d for d in self.data if d['id'] != id]

class Test(CleanUp, TestCase):

    def test(self):
        from zope.app.browser.undo import ZODBUndoManager
        um = ZODBUndoManager(StubDB())

        self.assertEqual(list(um.getUndoInfo()), testdata)

        um.undoTransaction(('3','4','5'))
        expected = testdata
        expected = [d for d in expected if (d['id'] not in ('3','4','5'))]

        self.assertEqual(list(um.getUndoInfo()), expected)

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')

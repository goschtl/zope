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
$Id: test_zodbundomanager.py,v 1.2 2004/03/18 14:33:22 philikon Exp $
"""

from time import time
from unittest import TestCase, main, makeSuite

from zope.testing.cleanup import CleanUp 
from zope.app.undo.undo import ZODBUndoManager

def dict(**kw): return kw

testdata = [
    dict(id='1', user_name='/ jim', time=time(), description='des 1'),
    dict(id='2', user_name='/ jim', time=time(), description='des 2'),
    dict(id='3', user_name='/ anthony', time=time(), description='des 3'),
    dict(id='4', user_name='/ jim', time=time(), description='des 4'),
    dict(id='5', user_name='/ anthony', time=time(), description='des 5'),
    dict(id='6', user_name='/ anthony', time=time(), description='des 6'),
    dict(id='7', user_name='/ jim', time=time(), description='des 7'),
    dict(id='8', user_name='/ anthony', time=time(), description='des 8'),
    dict(id='9', user_name='/ jim', time=time(), description='des 9'),
    dict(id='10', user_name='/ jim', time=time(), description='des 10'),
    ]
testdata.reverse()

class StubDB:

    def __init__(self):
        self.data = list(testdata)

    def undoInfo(self, first=0, last=-20, specification=None):
        if last < 0:
            last = first - last + 1
        # This code ripped off from zodb.storage.base.BaseStorage.undoInfo
        if specification:
            def filter(desc, spec=specification.items()):
                for k, v in spec:
                    if desc.get(k) != v:
                        return False
                return True
        else:
            filter = None
        if not filter:
            # handle easy case first
            data = self.data[first:last]
        else:
            data = []
            for x in self.data[first:]:
                if filter(x): 
                    data.append(x)
                if len(data) >= last:
                    break
        return data

    def undo(self, id):
        self.data = [d for d in self.data if d['id'] != id]

class Test(CleanUp, TestCase):

    def test(self):
        um = ZODBUndoManager(StubDB())

        self.assertEqual(list(um.getUndoInfo()), testdata)

        txid = [d['id'] for d in um.getUndoInfo(first=0,last=-3)]
        self.assertEqual(txid, ['10','9','8','7'])
        txid = [d['id'] for d in um.getUndoInfo(first=0,last=3)]
        self.assertEqual(txid, ['10','9','8'])
        txid = [d['id'] 
                for d in um.getUndoInfo(first=0, last=3, user_name='anthony')]
        self.assertEqual(txid, ['8','6','5'])
        txid = [d['id'] for d in um.getUndoInfo(user_name='anthony')]
        self.assertEqual(txid, ['8','6','5','3'])

        um.undoTransaction(('3','4','5'))

        expected = [d for d in testdata if (d['id'] not in ('3','4','5'))]
        self.assertEqual(list(um.getUndoInfo()), expected)

        txid = [d['id'] for d in um.getUndoInfo(user_name='anthony')]
        self.assertEqual(txid, ['8','6'])


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')

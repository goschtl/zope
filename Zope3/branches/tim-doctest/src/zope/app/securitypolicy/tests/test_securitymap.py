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
#############################################################################
"""Test ISecurityMap implementations

$Id$
"""
import unittest
from zope.interface.verify import verifyClass
from zope.app.securitypolicy.interfaces import ISecurityMap
from zope.app.securitypolicy.securitymap import SecurityMap
from zope.app.securitypolicy.securitymap import PersistentSecurityMap

class TestSecurityMap(unittest.TestCase):

    def testInterface(self):
        verifyClass(ISecurityMap, SecurityMap)

    def _getSecurityMap(self):
        return SecurityMap()

    def test_addCell(self):
        map = self._getSecurityMap()
        map.addCell(0, 0, 'aa')
        self.assertEqual(map._byrow[0][0], 'aa')
        self.assertEqual(map._bycol[0][0], 'aa')

        map.addCell(1, 0, 'ba')
        self.assertEqual(map._byrow[1][0], 'ba')
        self.assertEqual(map._bycol[0][1], 'ba')

        map.addCell(5, 3, 'fd')
        self.assertEqual(map._byrow[5][3], 'fd')
        self.assertEqual(map._bycol[3][5], 'fd')

    def test_addCell_noninteger(self):
        map = self._getSecurityMap()
        map.addCell(0.3, 0.4, 'entry')
        self.assertEqual(map._byrow[0.3][0.4], 'entry')
        self.assertEqual(map._bycol[0.4][0.3], 'entry')

        marker = object()
        map.addCell('a', 'b', marker)
        self.assertEqual(map._byrow['a']['b'], marker)
        self.assertEqual(map._bycol['b']['a'], marker)
        
    def test_delCell(self):
        map = self._getSecurityMap()
        map._byrow[0] = map._empty_mapping()
        map._bycol[1] = map._empty_mapping()
        map._byrow[0][1] = 'aa'
        map._bycol[1][0] = 'aa'
        map.delCell(0, 1)
        self.assertEqual(len(map._byrow.get(0)), 0) 
        self.assertEqual(len(map._bycol.get(1)), 0) 

    def test_queryCell(self):
        map = self._getSecurityMap()
        map._byrow[0] = map._empty_mapping()
        map._bycol[1] = map._empty_mapping()
        map._byrow[0][1] = 'aa'
        map._bycol[1][0] = 'aa'

        marker = object()
        self.assertEqual(map.queryCell(0, 1), 'aa')
        self.assertEqual(map.queryCell(1, 0), None)
        self.assertEqual(map.queryCell(1, 0, marker), marker)

    def test_getCell(self):
        map = self._getSecurityMap()
        map._byrow[0] = map._empty_mapping()
        map._bycol[1] = map._empty_mapping()
        map._byrow[0][1] = 'aa'
        map._bycol[1][0] = 'aa'

        self.assertEqual(map.getCell(0, 1), 'aa')
        self.assertRaises(KeyError, map.getCell, 1, 0)

    def test_getRow(self):
        map = self._getSecurityMap()
        map._byrow[0] = map._empty_mapping()
        map._byrow[0][1] = 'ab'
        map._byrow[0][2] = 'ac'
        map._byrow[1] = map._empty_mapping()
        map._byrow[1][1] = 'bb'
        map._bycol[1] = map._empty_mapping()
        map._bycol[1][0] = 'ab'
        map._bycol[1][1] = 'bb'
        map._bycol[2] = map._empty_mapping()
        map._bycol[2][0] = 'ac'

        self.assertEqual(map.getRow(0), [(1, 'ab'), (2, 'ac')])
        self.assertEqual(map.getRow(1), [(1, 'bb')])
        self.assertEqual(map.getRow(2), [])

    def test_getCol(self):
        map = self._getSecurityMap()
        map._byrow[0] = map._empty_mapping()
        map._byrow[0][1] = 'ab'
        map._byrow[0][2] = 'ac'
        map._byrow[1] = map._empty_mapping()
        map._byrow[1][1] = 'bb'
        map._bycol[1] = map._empty_mapping()
        map._bycol[1][0] = 'ab'
        map._bycol[1][1] = 'bb'
        map._bycol[2] = map._empty_mapping()
        map._bycol[2][0] = 'ac'

        self.assertEqual(map.getCol(1), [(0, 'ab'), (1, 'bb')])
        self.assertEqual(map.getCol(2), [(0, 'ac')])
        self.assertEqual(map.getCol(0), [])

    def test_getAllCells(self):
        map = self._getSecurityMap()
        map._byrow[0] = map._empty_mapping()
        map._byrow[0][1] = 'ab'
        map._byrow[0][2] = 'ac'
        map._byrow[1] = map._empty_mapping()
        map._byrow[1][1] = 'bb'
        map._bycol[1] = map._empty_mapping()
        map._bycol[1][0] = 'ab'
        map._bycol[1][1] = 'bb'
        map._bycol[2] = map._empty_mapping()
        map._bycol[2][0] = 'ac'

        self.assertEqual(map.getCol(1), [(0, 'ab'), (1, 'bb')])
        self.assertEqual(map.getCol(2), [(0, 'ac')])
        self.assertEqual(map.getCol(0), [])


class TestPersistentSecurityMap(TestSecurityMap):

    def testInterface(self):
        verifyClass(ISecurityMap, PersistentSecurityMap)

    def _getSecurityMap(self):
        return PersistentSecurityMap()


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSecurityMap),
        unittest.makeSuite(TestPersistentSecurityMap),
        ))

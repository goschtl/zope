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
$Id: test_zopecursor.py,v 1.3 2003/05/01 19:35:30 faassen Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.app.rdb import ZopeConnection
from zope.app.rdb import ZopeCursor
from zope.app.rdb.tests.stubs import *

class MyConnectionStub(ConnectionStub):
    def cursor(self):
        return MyCursorStub()


raw       = [['mano',      2,    'buvo batai'],
             ['dingo',     1,    'nerandu'],
             ['as su',     1,    'batuku'],
             ['eiti i',    None, 'galiu']]

converted = [['my',        42,   'shoes were'],
             ['were lost', 41,   "can't find"],
             ['with',      41,   'shoe'],
             ['go to',     None, 'I can']]


class MyCursorStub(CursorStub):

    description = ((None, 'string'), (None, 'int'), (None, 'foo'))

    def fetchone(self):
        return raw[:1]

    def fetchall(self):
        return raw

    def fetchmany(self, size=2):
        return raw[:size]


class MyTypeInfoStub(TypeInfoStub):

    def getConverter(self, type):

        def stringConverter(x):
            return {'mano': 'my',
                    'dingo': 'were lost',
                    'as su': 'with',
                    'eiti i': 'go to'}[x]

        def intConverter(x):
            if x is None:
                return None
            else:
                return x + 40

        def fooConverter(x):
            return {'buvo batai': 'shoes were',
                    'nerandu': "can't find",
                    'batuku': 'shoe',
                    'galiu': 'I can'}[x]

        return {'string': stringConverter,
                'int': intConverter,
                'foo': fooConverter}[type]


class ZopeCursorTests(TestCase):

    def setUp(self):
        zc = ZopeConnection(MyConnectionStub(), MyTypeInfoStub())
        self.cursor = ZopeCursor(zc.conn.cursor(), zc)

    def test_cursor_fetchone(self):
        results = self.cursor.fetchone()
        expected = converted[:1]
        self.assertEqual(results, expected,
                   'type conversion was not performed in cursor.fetchone:\n'
                   'got %r, expected %r' % (results, expected))

    def test_cursor_fetchmany(self):
        results = self.cursor.fetchmany()
        expected = converted[:2]
        self.assertEqual(results, expected,
                   'type conversion was not performed in cursor.fetchmany:\n'
                   'got      %r,\n'
                   'expected %r' % (results, expected))

    def test_cursor_fetchall(self):
        results = self.cursor.fetchall()
        expected = converted
        self.assertEqual(results, expected,
                   'type conversion was not performed in cursor.fetchall:\n'
                   'got      %r,\n'
                   'expected %r' % (results, expected))


def test_suite():
    return makeSuite(ZopeCursorTests)

if __name__=='__main__':
    main(defaultTest='test_suite')

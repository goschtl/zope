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
##############################################################################
"""SQL Expression Type Tests

$Id$
"""
import unittest

from zope.interface import implements
from zope.component.interfaces import IFactory
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.tales.tests.test_expressions import Data
from zope.tales.engine import Engine

from zope.app.tests import ztapi
from zope.app.rdb.tests.stubs import ConnectionStub
from zope.app.sqlexpr.sqlexpr import SQLExpr, NoConnectionSpecified

__metaclass__ = type

class ConnectionStub:

    def __init__(self):
        self._called = {}

    def cursor(self):
        return CursorStub()

    def answer(self):
        return 42

    def commit(self, *ignored):
        v = self._called.setdefault('commit',0)
        v += 1
        self._called['commit'] = v

    def rollback(self, *ignored):
        v = self._called.setdefault('rollback',0)
        v += 1
        self._called['rollback'] = v

class CursorStub:

    description = (('id', 0, 0, 0, 0, 0, 0),
                   ('name', 0, 0, 0, 0, 0, 0),
                   ('email', 0, 0, 0, 0, 0, 0))


    def fetchall(self, *args, **kw):
        return ((1, 'Stephan', 'srichter'),
               (2, 'Foo Bar', 'foobar'))

    def execute(self, operation, *args, **kw):
        assert operation == 'SELECT num FROM hitchhike'


class TypeInfoStub:
    paramstyle = 'pyformat'
    threadsafety = 0
    def getConverter(self, type):
        return lambda x: x


class FactoryStub:
    implements(IFactory)

    title = ''
    description = ''

    def __call__(self, *args, **kw):
        return ConnectionStub

    def getInterfaces(self):
        return TrueConnectionStub.__implements__


class SQLExprTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SQLExprTest, self).setUp()
        self.context = Data(vars = {'rdb': 'rdb_conn',
                                    'dsn': 'dbi://test'})
        self.engine = Engine
        
        ztapi.provideUtility(IFactory, FactoryStub(), 'rdb_conn')

    def test_exprUsingRDBAndDSN(self):
        expr = SQLExpr('name', 'SELECT num FROM hitchhike', self.engine)
        result = expr(self.context)
        self.assertEqual(1, result[0].id)
        self.assertEqual('Stephan', result[0].name)
        self.assertEqual('srichter', result[0].email)
        self.assertEqual('Foo Bar', result[1].name)

    def test_noRDBSpecs(self):
        expr = SQLExpr('name', 'SELECT num FROM hitchhike', self.engine)
        self.assertRaises(NoConnectionSpecified, expr, Data(vars={}))

def test_suite():
    return unittest.TestSuite((unittest.makeSuite(SQLExprTest),))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())

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

$Id: test_sqlexpr.py 26878 2004-08-03 16:25:34Z jim $
"""
import unittest

from zope.interface import implements
from zope.component.factory import Factory
from zope.component.interfaces import IFactory
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.tales.tests.test_expressions import Data
from zope.tales.engine import Engine

from zope.app.testing import ztapi
from zope.app.rdb.interfaces import IZopeDatabaseAdapter, IZopeConnection
from zope.app.rdb.tests.stubs import ConnectionStub
from zope.app.sqlexpr.sqlexpr import SQLExpr, ConnectionError


class AdapterStub(object):
    implements(IZopeDatabaseAdapter)

    def __init__(self, dsn):
        return

    def __call__(self):
        return ConnectionStub()

class ConnectionStub(object):
    implements(IZopeConnection)

    def __init__(self):
        self._called = {}

    def cursor(self):
        return CursorStub()

class CursorStub(object):

    description = (('id', 0, 0, 0, 0, 0, 0),
                   ('name', 0, 0, 0, 0, 0, 0),
                   ('email', 0, 0, 0, 0, 0, 0))


    def fetchall(self, *args, **kw):
        return ((1, 'Stephan', 'srichter'),
               (2, 'Foo Bar', 'foobar'))

    def execute(self, operation, *args, **kw):
        if operation != 'SELECT num FROM hitchhike':
            raise AssertionError(operation, 'SELECT num FROM hitchhike')


class SQLExprTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SQLExprTest, self).setUp()
        ztapi.provideUtility(IFactory, Factory(AdapterStub),
                             'zope.da.Stub')
        ztapi.provideUtility(IFactory, Factory(lambda x: None),
                             'zope.Fake')
        ztapi.provideUtility(IZopeDatabaseAdapter, AdapterStub(''),
                             'test')

    def test_exprUsingRDBAndDSN(self):
        context = Data(vars = {'rdb': 'zope.da.Stub', 'dsn': 'dbi://test'})
        expr = SQLExpr('name', 'SELECT num FROM hitchhike', Engine)
        result = expr(context)
        self.assertEqual(1, result[0].id)
        self.assertEqual('Stephan', result[0].name)
        self.assertEqual('srichter', result[0].email)
        self.assertEqual('Foo Bar', result[1].name)

    def test_exprUsingSQLConn(self):
        context = Data(vars = {'sql_conn': 'test'})
        expr = SQLExpr('name', 'SELECT num FROM hitchhike', Engine)
        result = expr(context)
        self.assertEqual(1, result[0].id)
        self.assertEqual('Stephan', result[0].name)
        self.assertEqual('srichter', result[0].email)
        self.assertEqual('Foo Bar', result[1].name)

    def test_exprUsingRDBAndDSN_InvalidFactoryId(self):
        context = Data(vars = {'rdb': 'zope.da.Stub1', 'dsn': 'dbi://test'})
        expr = SQLExpr('name', 'SELECT num FROM hitchhike', Engine)
        self.assertRaises(ConnectionError, expr, context)

    def test_exprUsingRDBAndDSN_WrongFactory(self):
        context = Data(vars = {'rdb': 'zope.Fake', 'dsn': 'dbi://test'})
        expr = SQLExpr('name', 'SELECT num FROM hitchhike', Engine)
        self.assertRaises(ConnectionError, expr, context)

    def test_exprUsingSQLConn_WrongId(self):
        context = Data(vars = {'sql_conn': 'test1'})
        expr = SQLExpr('name', 'SELECT num FROM hitchhike', Engine)
        self.assertRaises(ConnectionError, expr, context)

    def test_noRDBSpecs(self):
        expr = SQLExpr('name', 'SELECT num FROM hitchhike', Engine)
        self.assertRaises(ConnectionError, expr, Data(vars={}))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SQLExprTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

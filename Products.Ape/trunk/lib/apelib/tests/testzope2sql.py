##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Test of storing objects in relational databases via ZODB

$Id$
"""

import unittest
import sys

from transaction import get as get_transaction

from apelib.zodb3.db import ApeDB
from apelib.zodb3.storage import ApeStorage
from apelib.zodb3.resource import StaticResource
from apelib.zope2.mapper import load_conf
from apelib.tests.zope2testbase import Zope2TestBase


conf = None

class Zope2SQLTests (Zope2TestBase):

    dbapi_module = None  # Name of the Database API module (required)
    class_name = None
    connect_expression = ''

    def get_connection(self):
        pos = self.class_name.rfind('.')
        m = self.class_name[:pos]
        cn = self.class_name[pos + 1:]
        c = getattr(__import__(m, {}, {}, ('__doc__',)), cn)
        return c(self.dbapi_module, self.connect_expression, prefix="apetest_")

    def setUp(self):
        global conf
        if conf is None:
            conf = load_conf('sql')
        conn = self.get_connection()
        self.conf = conf
        resource = StaticResource(self.conf)
        self.conns = {'db': conn}
        storage = ApeStorage(resource, self.conns, clear_all=1,
                             debug_conflicts=1)
        self.storage = storage
        self.assertEqual(conn.transaction_started, False)
        self.db = ApeDB(storage, resource)
        try:
            c = self.db.open()
            try:
                if not c.root().has_key('Application'):
                    from OFS.Application import Application
                    c.root()['Application'] = Application()
                    get_transaction().commit()
            finally:
                get_transaction().abort()
                c.close()
        except:
            self.db.close()
            raise
        self.assertEqual(conn.transaction_started, False)

    def clear(self):
        self.storage.init_databases(clear_all=1)

    def tearDown(self):
        get_transaction().abort()
        self.clear()
        self.db.close()

    def test_connect(self):
        # Tests the setUp/tearDown methods
        pass

    def test_commit_transaction_after_read(self):
        # After a read, the database transaction should not remain
        # open.
        conn = self.db.open()
        try:
            conn._resetCache()
            self.assertEqual(self.conns['db'].transaction_started, False)
            app = conn.root()['Application']
            app.getId()
            self.assertEqual(self.conns['db'].transaction_started, True)
            get_transaction().commit()
            self.assertEqual(self.conns['db'].transaction_started, False)
        finally:
            conn.close()


class PsycopgTests (Zope2SQLTests, unittest.TestCase):
    dbapi_module = 'psycopg'
    class_name = 'apelib.sql.postgresql.PostgreSQLConnection'
    connect_expression = 'connect("")'


class MySQLTests (Zope2SQLTests, unittest.TestCase):
    dbapi_module = 'MySQLdb'
    class_name = 'apelib.sql.mysql.MySQLConnection'
    connect_expression = 'connect(db="ape")'


def test_suite():
    """Makes a test suite for the available databases."""
    suite = unittest.TestSuite()
    for k, v in globals().items():
        mname = getattr(v, 'dbapi_module', None)
        if mname is not None:
            try:
                __import__(mname, {}, {}, ('__doc__',))
            except ImportError:
                sys.stderr.write('Warning: could not import %s. '
                                 'Skipping %s.\n'
                                 % (repr(mname), k))
            else:
                case = v('test_connect')
                conn = case.get_connection()
                try:
                    conn.connect()
                    conn.close()
                except conn.module.Error:
                    sys.stderr.write('Warning: could not open a '
                                     'connection using %s. Skipping %s.\n'
                                     % (repr(mname), k))
                else:
                    suite.addTest(unittest.makeSuite(v, 'test'))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

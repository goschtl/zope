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
"""Gadfly database adapter unit tests.

$Id: testAdapter.py,v 1.1 2002/11/05 17:34:40 alga Exp $
"""

import os
import tempfile
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.RDB.ZopeDatabaseAdapter import DatabaseAdapterError

try:
    from tempfile import mkdtemp
except ImportError:
    import errno

    def mkdtemp(suffix=""):
        """Poor man's version of tempfile.mkdtemp from Python 2.3"""

        for seq in xrange(1000):
            name = tempfile.mktemp(suffix)
            try:
                os.mkdir(name, 0700)
                return name
            except IOError, e:
                if e.errno == errno.EEXIST:
                    continue
                raise

        raise IOError(errno.EEXIST, "No usable temporary directory name found")


class GadflyTestBase(TestCase):

    def setUp(self):
    	TestCase.setUp(self)
	self.tempdir = None

    def tearDown(self):
	TestCase.tearDown(self)
	if self.tempdir:
	    os.rmdir(self.tempdir)

    def getGadflyRoot(self):
	# note that self is GadflyTestBase here
	if not self.tempdir:
	    self.tempdir = mkdtemp('gadfly')
	return self.tempdir
	
    def _create(self, *args):
    	from Zope.App.RDB.GadflyDA.Adapter import GadflyAdapter
	obj = GadflyAdapter(*args)
	obj._getGadflyRoot = self.getGadflyRoot
	return obj


class TestGadflyAdapter(GadflyTestBase):
    """Test incorrect connection strings"""

    def test__connection_factory_nonexistent(self):
        # Should raise an exception on nonexistent dirs.
        a = self._create("dbi://demo;dir=nonexistent")
        self.assertRaises(DatabaseAdapterError, a._connection_factory)

    def test__connection_factory_bad_dsn(self):
        a = self._create("dbi://user:pass/demo;dir=nonexistent")
        self.assertRaises(DatabaseAdapterError, a._connection_factory)

        a = self._create("dbi://localhost:1234/demo;dir=nonexistent")
        self.assertRaises(DatabaseAdapterError, a._connection_factory)


class TestGadflyAdapterNew(GadflyTestBase):
    """Test with nonexistent databases"""

    def test__connection_factory_create(self):
        # Should create a database if the directory is empty.
        a = self._create("dbi://demo;dir=test")
        conn = a._connection_factory()
        conn.rollback()         # is it really a connection?

    def test__connection_factory_existing(self):
        # Should fail gracefully if the directory is a file.
        open(os.path.join(self.getGadflyRoot(), "regular"), "w").close()
        a = self._create("dbi://demo;dir=regular")
        self.assertRaises(DatabaseAdapterError, a._connection_factory)

    def setUp(self):
        # Create a directory for the database.
	GadflyTestBase.setUp(self)
	dir = self.getGadflyRoot()
        os.mkdir(os.path.join(dir, "test"))

    def tearDown(self):
        # Remove the files and directories created.
	dir = self.getGadflyRoot()
        try: os.unlink(os.path.join(dir, "test", "demo.gfd"))
        except: pass
        os.rmdir(os.path.join(dir, "test"))
        try: os.unlink(os.path.join(dir, "regular"))
        except: pass
	GadflyTestBase.tearDown(self)
        

class TestGadflyAdapterDefault(GadflyTestBase):
    """Test with pre-existing databases"""

    def test__connection_factory_create(self):
        # Should create a database if the directory is empty.
        a = self._create("dbi://demo")
        conn = a._connection_factory()
        conn.rollback()         # is it really a connection?

    def test__connection_factory_reopen(self):
        # Should open an existing database.
        a = self._create("dbi://demo")
        conn = a._connection_factory()
        conn.rollback()         # is it really a connection?
        conn.close()

        conn = a._connection_factory() 
        conn.rollback()         # is it really a connection?

    def setUp(self):
        # Create a directory for the database.
	GadflyTestBase.setUp(self)
	dir = self.getGadflyRoot()
        os.mkdir(os.path.join(dir, "demo"))

    def tearDown(self):
        # Remove the files and directories created.
	dir = self.getGadflyRoot()
        try: os.unlink(os.path.join(dir, "demo", "demo.gfd"))
        except: pass
        os.rmdir(os.path.join(dir, "demo"))
	GadflyTestBase.tearDown(self)
        

def test_suite():
    return TestSuite((
        makeSuite(TestGadflyAdapter),
        makeSuite(TestGadflyAdapterNew),
        makeSuite(TestGadflyAdapterDefault),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

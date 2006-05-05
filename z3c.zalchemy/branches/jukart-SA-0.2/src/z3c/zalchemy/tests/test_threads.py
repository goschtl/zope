import unittest
import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import setup
from zope.app.testing.placelesssetup import PlacelessSetup
import os, tempfile
import shutil
import sqlalchemy
from z3c.zalchemy.datamanager import AlchemyEngineUtility
from zope.component import provideUtility
import transaction
from z3c.zalchemy.datamanager import beforeTraversal
class A(object):
    pass


class TestThreads(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestThreads,self).setUp()
        self.tmpDir = tempfile.mkdtemp()
        self.dbFile = os.path.join(self.tmpDir,'z3c.alchemy.test.db')

    def tearDown(self):
        shutil.rmtree(self.tmpDir)
        super(TestThreads,self).tearDown()

    def testReconnect(self):

        """tests if we can get data back from a table"""
        
        engineUtil = AlchemyEngineUtility(
            'sqlite',
            dns='sqlite://filename=%s.1' % self.dbFile,
            )
        provideUtility(engineUtil, name='1')
        
        aTable = sqlalchemy.Table(
            'aTable',sqlalchemy.ext.proxy.ProxyEngine(),
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('value', sqlalchemy.Integer),
            )
        sqlalchemy.assign_mapper(A, aTable)
        engineUtil.addTable(aTable,create=True)

        txn = transaction.begin()
        beforeTraversal(None)

        a = A()
        a.value = 123
        transaction.get().commit()

        txn = transaction.begin()
        beforeTraversal(None)

        a = A.get(1)
        a.value




def test_suite():
    return unittest.TestSuite((
        #unittest.makeSuite(TestThreads),
        ))
    
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

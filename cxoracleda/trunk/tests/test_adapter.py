"""Unit tests for cxoracleda
"""
from unittest import TestCase, TestSuite, main, makeSuite
from cxoracleda.adapter import DatabaseAdapter
from zope.app import zapi
from zope.app.rdb.interfaces import IManageableZopeDatabaseAdapter,IZopeDatabaseAdapter
from zope.app.testing import setup
import os
propFile = os.path.join(os.environ.get('HOME'),"etc/zope/cxoracleda/testproperties.py")

try:
    execfile(propFile)
except:
    raise "Local property file not found",propFile





class TestBase(TestCase):
    
    def setUp(self):
        super(TestBase,self).setUp()
        self.da = DatabaseAdapter(CONNECTION_STRING)
        
    
    def test_reg(self):
        root = setup.placefulSetUp(site=True)
        sm = root.getSiteManager()
        setup.addUtility(sm, 'test_db_adapter',
                         IManageableZopeDatabaseAdapter, self.da)
        da, = list(zapi.getAllUtilitiesRegisteredFor(IManageableZopeDatabaseAdapter))
        self.assertEqual(da,self.da)

    def test_it(self):
        da = self.da
        da.connect()
        conn = da()
        cursor = conn.cursor()
        cursor.execute('select 100 from dual')
        res = cursor.fetchall()
        self.assertEqual(res,[[100]])
        cursor.close()
        da.disconnect()
    

def test_suite():
    return TestSuite((
            makeSuite(TestBase),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

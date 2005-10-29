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
    
    def test_unicode(self):

        da = self.da
        da.connect()
        conn = da()
        cursor = conn.cursor()
        cursor.execute("select 'abc' from dual")
        res = cursor.fetchall()
        self.assertEqual(res,[[u'abc']])
        cursor.close()
        da.disconnect()

    def test_date(self):

        da = self.da
        da.connect()
        conn = da()
        cursor = conn.cursor()
        from datetime import datetime
        d = datetime(1998,5,31,8,5)
        cursor.execute("""select
        to_date('1998/05/31:08:05:00AM', 'yyyy/mm/dd:hh:mi:ssam')
        from dual""")
        res = cursor.fetchall()
        v = res[0][0]
        assert(callable( v.strftime))
        self.assertEqual(type(v),type(d))
        self.assertEqual(res,[[d]])
        cursor.close()
        da.disconnect()






def test_suite():
    return TestSuite((
            makeSuite(TestBase),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

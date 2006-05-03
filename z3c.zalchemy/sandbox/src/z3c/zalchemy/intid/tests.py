import unittest
import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import setup
import os, tempfile
import shutil
from z3c.zalchemy.datamanager import AlchemyEngineUtility
from zope import component
import sqlalchemy

def setUp(test):
    setup.placefulSetUp()
    test.tmpDir = tempfile.mkdtemp()
    dbFile = os.path.join(test.tmpDir,'z3c.alchemy.test.db')
    
    engineUtil = AlchemyEngineUtility(
        'sqlite',dns='sqlite://filename=%s.1' % dbFile)
    component.provideUtility(engineUtil, name='sqlite')
    test.globs['engine'] = sqlalchemy.ext.proxy.ProxyEngine()
    test.globs['engineUtil'] = engineUtil
    

def tearDown(test):
    shutil.rmtree(test.tmpDir)
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('keyreference.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))



if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

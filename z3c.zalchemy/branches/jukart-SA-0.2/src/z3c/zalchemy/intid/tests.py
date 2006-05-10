import unittest
import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import setup
import os, tempfile
import shutil
from z3c.zalchemy.datamanager import AlchemyEngineUtility
import z3c.zalchemy.testing
from zope import component

def setUp(test):
    setup.placefulSetUp()
    z3c.zalchemy.testing.setUp(test)
    test.tmpDir = tempfile.mkdtemp()
    dbFile = os.path.join(test.tmpDir,'z3c.zalchemy.test.intid.db')
    
    engineUtil = AlchemyEngineUtility(
        'database','sqlite:///%s' % dbFile)
    component.provideUtility(engineUtil)
    test.globs['engineUtil'] = engineUtil
    

def tearDown(test):
    z3c.zalchemy.testing.tearDown(test)
    setup.placefulTearDown()
    shutil.rmtree(test.tmpDir)


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('keyreference.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))



if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

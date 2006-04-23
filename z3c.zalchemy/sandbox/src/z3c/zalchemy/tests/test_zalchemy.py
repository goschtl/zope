import unittest
import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import setup
import os, tempfile
import shutil


def setUp(test):
    setup.placefulSetUp()
    test.tmpDir = tempfile.mkdtemp()
    test.globs['dbFile'] = os.path.join(test.tmpDir,'z3c.alchemy.test.db')

def tearDown(test):
    shutil.rmtree(test.tmpDir)
    setup.placefulTearDown()



def test_suite():
    return unittest.TestSuite((
        DocFileSuite('../README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('TRANSACTION.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))



if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


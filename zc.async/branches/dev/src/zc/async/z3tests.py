import os
import unittest
from zope.testing import doctest, module

import zc.async.tests

def setUp(test):
    zc.async.tests.modSetUp(test)
    # make the uuid stable for these tests
    f = open(os.path.join(
        os.environ["INSTANCE_HOME"], 'etc', 'uuid.txt'), 'w')
    f.writelines(('d10f43dc-ffdf-11dc-abd4-0017f2c49bdd',)) # ...random...
    f.close()
    zc.async.instanceuuid.UUID = zc.async.instanceuuid.getUUID()

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'monitor.txt',
            setUp=setUp, tearDown=zc.async.tests.modTearDown,
            optionflags=doctest.INTERPRET_FOOTNOTES),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

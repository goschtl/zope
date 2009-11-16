import unittest

from zope.testing import doctest, module
import zope.component.testing

def modSetUp(test):
    zope.component.testing.setUp(test)
    module.setUp(test, 'zc.twist.README')

def modTearDown(test):
    module.tearDown(test)
    zope.component.testing.tearDown(test)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=modSetUp, tearDown=modTearDown,
            optionflags=doctest.INTERPRET_FOOTNOTES),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

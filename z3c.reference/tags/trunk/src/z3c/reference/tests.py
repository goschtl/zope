import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from zope.app.testing import setup
from zope import component
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.keyreference.testing import SimpleKeyReference
def setUp(test):
    setup.placefulSetUp()
    component.provideAdapter(SimpleKeyReference)
    component.provideAdapter(ZDCAnnotatableAdapter,
                             provides=IWriteZopeDublinCore)

def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    
    return unittest.TestSuite(
        (
        DocFileSuite('README.txt',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


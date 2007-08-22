import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from zope.app.testing import setup
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope import component
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.keyreference.testing import SimpleKeyReference
from lovely.relation import configurator


def setUp(test):
    root = setup.placefulSetUp(True)
    test.globs['root'] = root
    util = configurator.SetUpO2OStringTypeRelationships(root)
    util({})
    component.provideAdapter(SimpleKeyReference)
    component.provideAdapter(ZDCAnnotatableAdapter,
                             provides=IWriteZopeDublinCore)
    intids = IntIds()
    component.provideUtility(intids, IIntIds)

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


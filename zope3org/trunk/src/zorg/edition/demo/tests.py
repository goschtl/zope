import unittest
from zope.testing.doctest import DocFileSuite, DocTestSuite
from zope.annotation.interfaces import IAnnotatable, IAttributeAnnotatable

from zope.app.testing import placelesssetup
from zope.app.testing import ztapi

from zope.app.testing.setup import setUpAnnotations
from zope.dublincore.interfaces import IZopeDublinCore
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.interface.declarations import classImplements


from zorg.edition.demo.vproposal import VProposal


def setUp(test):
    placelesssetup.setUp(test)
    setUpAnnotations()
    ztapi.provideAdapter(IAnnotatable, IZopeDublinCore,
                         ZDCAnnotatableAdapter)
    classImplements(VProposal,IAttributeAnnotatable)    
 
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocFileSuite('vproposal.txt',setUp=setUp,
                                tearDown=placelesssetup.tearDown))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

import unittest
from zope.testing.doctest import DocFileSuite, DocTestSuite
from zope.app.tests import placelesssetup
from zope.app.tests import ztapi

from vproposal import VProposal
from zope.app.tests.setup import setUpAnnotations
from zope.app.annotation.interfaces import IAnnotatable, IAttributeAnnotatable
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.interface.declarations import classImplements

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


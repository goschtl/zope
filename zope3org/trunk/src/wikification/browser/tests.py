import unittest

import zope
import zope.component

from zope.testing import doctest, doctestunit
from zope.app.testing import ztapi
from zope.app.testing.setup import placefulSetUp, placefulTearDown

from zope.interface import classImplements
from zope.app import zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.annotation.interfaces import IAnnotations
from zope.app.annotation.interfaces import IAnnotatable
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.container.interfaces import IContained


import wikification.tests

def setUpBrowserTests(test) :

    wikification.tests.setUpWikification(test)
    
   
    
def tearDownBrowserTests(test) :

    wikification.tests.tearDownWikification(test)

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS
    globs = {'zapi': zope.app.zapi,
             'pprint': doctestunit.pprint,
             'TestRequest': zope.publisher.browser.TestRequest}
 
    return unittest.TestSuite((
    
        doctest.DocTestSuite("wikification.browser.wikipage", 
                                setUp=setUpBrowserTests, 
                                tearDown=tearDownBrowserTests,
                                optionflags=optionflags
                             ),
                             
 #        doctest.DocFileSuite("README.txt", 
#                                 setUp=setUpBrowserTests, 
#                                 tearDown=tearDownBrowserTests,
#                                 globs=globs,
#                                 optionflags=optionflags
#                              ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

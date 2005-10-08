import unittest

import zope
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

def setUpBrowserTests(test) :
    pass
   
    
def tearDownBrowserTests(test) :
    pass

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite("README.txt", 
                                setUp=setUpBrowserTests, 
                                tearDown=tearDownBrowserTests,
                                globs={'zapi': zope.app.zapi,
                                       'pprint': doctestunit.pprint,
                                       'TestRequest': zope.publisher.browser.TestRequest                                
                                        },
                                optionflags=doctest.NORMALIZE_WHITESPACE+
                                            doctest.ELLIPSIS
                             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

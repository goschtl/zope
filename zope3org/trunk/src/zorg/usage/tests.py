##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: tests.py 41271 2006-01-11 17:02:07Z oestermeier $
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.testing import doctest, doctestunit

import zope.app.zapi
import zope.component.testing
         
       
def test_suite():

    return unittest.TestSuite((
        #doctest.DocTestSuite(setUp=setUp, tearDown=tearDown)),
        
        doctest.DocFileSuite("README.txt", 
                    setUp=zope.component.testing.setUp, 
                    tearDown=zope.component.testing.tearDown,
                    globs={'zapi': zope.app.zapi,
                           'pprint': doctestunit.pprint,
                           'TestRequest': zope.publisher.browser.TestRequest                                
                          },
                    optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS),        
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')    
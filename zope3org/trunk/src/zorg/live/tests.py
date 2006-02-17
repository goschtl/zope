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

$Id: tests.py 39651 2005-10-26 18:36:17Z oestermeier $
"""

import unittest, zope

from zope.testing import doctest, doctestunit

from zope.app import zapi
from zope.app.testing import ztapi
from zope.publisher.browser import TestRequest

from zorg.live.testing import placelesssetup
  
      

globs = {'zapi': zapi,
            'ztapi': ztapi,
            'zope':zope,
            'pprint': doctestunit.pprint,
            'TestRequest':TestRequest}
            
optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS           
        
        
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt', 
                                setUp=placelesssetup.setUp, 
                                tearDown=placelesssetup.tearDown,
                                globs=globs,
                                optionflags=optionflags
                             ),
                             
        doctest.DocTestSuite('zorg.live.page.page',
                                setUp=placelesssetup.setUp, 
                                tearDown=placelesssetup.tearDown,
                                optionflags=optionflags
                             ),

        doctest.DocTestSuite('zorg.live.page.client',
                                setUp=placelesssetup.setUp, 
                                tearDown=placelesssetup.tearDown,
                                optionflags=optionflags
                             ),


        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: test_pagetemplateresource.py,v 1.2 2003/11/21 17:12:10 jim Exp $
"""

import os
from unittest import TestCase, main, makeSuite

from zope.exceptions import NotFoundError
from zope.app.tests import ztapi
from zope.security.checker import NamesChecker
from zope.publisher.browser import TestRequest

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.publisher.browser.pagetemplateresource import \
     PageTemplateResourceFactory
from zope.app.interfaces.traversing import ITraversable
from zope.app.traversing.adapters import DefaultTraversable
import zope.app.publisher.browser.tests as p

test_directory = os.path.split(p.__file__)[0]

checker = NamesChecker(
    ('__call__', 'request', 'publishTraverse')
    )

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        ztapi.provideAdapter(None, ITraversable, DefaultTraversable)

    def testNoTraversal(self):
        path = os.path.join(test_directory, 'testfiles', 'test.pt')
        request = TestRequest()
        resource = PageTemplateResourceFactory(path, checker)(request)
        self.assertRaises(NotFoundError, resource.publishTraverse,
                          resource.request, ())

    def testCall(self):
        path = os.path.join(test_directory, 'testfiles', 'testresource.pt')
        test_data = "Foobar"
        request = TestRequest(test_data=test_data)
        resource = PageTemplateResourceFactory(path, checker)(request)
        self.assert_(resource(), test_data)        

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')

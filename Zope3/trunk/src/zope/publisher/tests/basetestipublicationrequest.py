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

Revision information:
$Id: basetestipublicationrequest.py,v 1.3 2003/08/08 18:07:21 jim Exp $
"""

import sys
from zope.interface.verify import verifyObject
from zope.publisher.interfaces import IPublicationRequest


class BaseTestIPublicationRequest:
    def testVerifyIPublicationRequest(self):
        verifyObject(IPublicationRequest, self._Test__new())

    def testHaveCustomTestsForIPublicationRequest(self):
        # Make sure that tests are defined for things we can't test here
        self.test_IPublicationRequest_getPositionalArguments

    def testTraversalStack(self):
        request = self._Test__new()
        stack = ['Engineering', 'ZopeCorp']
        request.setTraversalStack(stack)
        self.assertEqual(list(request.getTraversalStack()), stack)

    def testHoldCloseAndGetResponse(self):
        request = self._Test__new()

        response = request.response
        rcresponse = sys.getrefcount(response)

        resource = object()
        rcresource = sys.getrefcount(resource)

        request.hold(resource)

        self.failUnless(sys.getrefcount(resource) > rcresource)

        request.close()
        self.failUnless(sys.getrefcount(response) < rcresponse)
        self.assertEqual(sys.getrefcount(resource), rcresource)

    def testSkinManagement(self):
        request = self._Test__new()
        self.assertEqual(request.getPresentationSkin(), '')
        skin = 'terse'
        request.setPresentationSkin(skin)
        self.assertEqual(request.getPresentationSkin(), skin)

    def test_getPresentationType(self):
        type = self._Test__expectedViewType()
        request = self._Test__new()
        self.assertEqual(request.getPresentationType(), type)

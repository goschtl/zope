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

$Id: test_viewservice.py,v 1.1 2003/06/23 16:43:10 mgedmin Exp $
"""

import unittest
from zope.interface import Interface, implements
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component.exceptions import ComponentLookupError

__metaclass__ = type

class ISomePresentation(Interface):
    pass

class ISomeOtherPresentation(Interface):
    pass

class ISomeObject(Interface):
    pass

class ISomeOtherObject(Interface):
    pass

class ObjectStub:
    implements(ISomeObject)

class OtherObjectStub:
    implements(ISomeOtherObject)

class RequestStub:
    _presentationType = ISomePresentation
    _presentationSkin = 'default'
    def getPresentationType(self):
        return self._presentationType
    def getPresentationSkin(self):
        return self._presentationSkin

class ViewStub:
    def __init__(self, context, request):
        self.context = context
        self.request = request


class TestGlobalViewService(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)

    def testGetView(self):
        from zope.component.view import GlobalViewService
        service = GlobalViewService()
        service.provideView(ISomeObject, 'sunglasses', ISomePresentation,
                            ViewStub)

        obj = ObjectStub()
        rq = RequestStub()
        view = service.getView(obj, 'sunglasses', rq)
        self.assert_(view.context is obj)
        self.assert_(view.request is rq)

        self.assertRaises(ComponentLookupError,
                          service.getView, obj, 'moonglasses', rq)

        rq._presentationType = ISomeOtherPresentation
        self.assertRaises(ComponentLookupError,
                          service.getView, obj, 'sunglasses', rq)

        obj = OtherObjectStub()
        rq = RequestStub()
        self.assertRaises(ComponentLookupError,
                          service.getView, obj, 'sunglasses', rq)

    # XXX test other methods as well


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestGlobalViewService)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())

##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Unit test for field index browser views

$Id$
"""
import unittest
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.component import getGlobalServices
from zope.exceptions import NotFoundError

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.servicenames import HubIds
from zope.app.hub.interfaces import IObjectHub
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.index.browser.field.control import ControlView

class DublinCoreStub:
    implements(IZopeDublinCore)

    def __init__(self, title):
        self.title = title

class ObjectHubStub:
    implements(IObjectHub)

    def getPath(self, id):
        return {101: '/a', 102: '/b'}[id]

    def getObject(self, id):
        if id == 102:
            return DublinCoreStub(title='Foo')
        else:
            raise NotFoundError

class FieldIndexStub:

    def search(self, values):
        assert values == 'xyzzy'
        return [101, 102]

class TestControlView(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestControlView, self).setUp()
        service_manager = getGlobalServices()
        service_manager.defineService(HubIds, IObjectHub)
        service_manager.provideService(HubIds, ObjectHubStub())

    def test_query(self):
        index = FieldIndexStub()
        request = TestRequest()
        view = ControlView(index, request)
        request.form['queryText'] = 'xyzzy'
        results = view.query()
        self.assertEquals(results, {'results': [
                                            {'location': '/a'},
                                            {'location': '/b', 'title': 'Foo'}
                                        ],
                                    'nresults': 2,
                                    'first': 1,
                                    'last': 2,
                                    'total': 2})


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestControlView))
    return suite


if __name__ == '__main__':
    unittest.main()

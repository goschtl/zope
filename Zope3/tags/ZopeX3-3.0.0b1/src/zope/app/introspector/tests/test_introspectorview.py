##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Introspector view tests

$Id$
"""

import unittest
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.publisher.browser import TestRequest
from zope.app.tests import setup
from zope.interface import Interface, directlyProvidedBy
from zope.interface import directlyProvides, implements
from zope.app.component.interface import provideInterface
from zope.app.tests import ztapi
from zope.app.introspector.interfaces import IIntrospector
from zope.app.introspector import Introspector

class I1(Interface):
    pass

id = 'zope.app.introspector.tests.test_introspectorview.I1'

class I2(Interface):
    pass

id2 = 'zope.app.introspector.tests.test_introspectorview.I2'

class TestIntrospectorView(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.rootFolder = setup.buildSampleFolderTree()
        mgr = setup.createServiceManager(self.rootFolder)
        provideInterface(id, I1)
        provideInterface(id2, I2)
        ztapi.provideAdapter(None, IIntrospector, Introspector)


    def test_getInterfaceURL(self):
        from zope.app.introspector.browser import IntrospectorView

        request = TestRequest()
        view = IntrospectorView(self.rootFolder, request)

        self.assertEqual(
            view.getInterfaceURL(id),
            'http://127.0.0.1/++etc++site/interfacedetail.html?id=%s'
            % id)

        self.assertEqual(view.getInterfaceURL('zope.app.INonexistent'),
                         '')

    def test_update(self):
        from zope.app.introspector.browser import IntrospectorView

        class Context:
            implements(Interface)

        context = Context()
        request = TestRequest()
        request.form['ADD']= ''
        request.form['add_%s' % id] = 'on'
        request.form['add_%s' % id2] = 'on'
        view = IntrospectorView(context, request)
        view.update()
        self.assert_(I1 in directlyProvidedBy(context))
        self.assert_(I2 in directlyProvidedBy(context))

        context = Context()
        directlyProvides(context, I1)
        request = TestRequest()
        request.form['REMOVE']= ''
        request.form['rem_%s' % id] = 'on'
        view = IntrospectorView(context, request)
        view.update()
        self.assertEqual(tuple(directlyProvidedBy(context)), ())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIntrospectorView))
    return suite


if __name__ == '__main__':
    unittest.main()

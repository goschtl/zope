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
"""Introspector view tests

$Id: test_introspector.py,v 1.3 2003/11/21 17:11:59 jim Exp $
"""

import unittest
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.interface import LocalInterfaceService
from zope.app.services.servicenames import Interfaces
from zope.publisher.browser import TestRequest
from zope.app.tests import setup
from zope.interface import Interface, directlyProvidedBy
from zope.interface import directlyProvides, implements
from zope.app.component.globalinterfaceservice import provideInterface
from zope.app.tests import ztapi
from zope.app.interfaces.introspector import IIntrospector
from zope.app.introspector import Introspector

class I1(Interface):
    pass

id = 'zope.app.browser.tests.test_introspector.I1'

class I2(Interface):
    pass

id2 = 'zope.app.browser.tests.test_introspector.I2'

class TestIntrospectorView(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.rootFolder = setup.buildSampleFolderTree()
        mgr = setup.createServiceManager(self.rootFolder)
        service = setup.addService(mgr, Interfaces, LocalInterfaceService())

        provideInterface(id, I1)
        provideInterface(id2, I2)
        ztapi.provideAdapter(None, IIntrospector, Introspector)


    def test_getInterfaceURL(self):
        from zope.app.browser.introspector import IntrospectorView

        request = TestRequest()
        view = IntrospectorView(self.rootFolder, request)

        self.assertEqual(
            view.getInterfaceURL(id),
            'http://127.0.0.1/++etc++site/default/Interfaces/detail.html?id=%s'
            % id)

        self.assertEqual(view.getInterfaceURL('zope.app.INonexistent'),
                         '')

    def test_update(self):
        from zope.app.browser.introspector import IntrospectorView

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

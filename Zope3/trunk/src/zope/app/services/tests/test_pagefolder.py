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
"""View package tests.

$Id: test_pagefolder.py,v 1.7 2003/07/02 22:11:08 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.tests import setup
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.pagefolder import PageFolder, PageFolderContextDecorator
from zope.app.interfaces.services.pagefolder import IPageFolder
from zope.app.interfaces.context import IZopeContextWrapper
from zope.app.traversing import traverse
from zope.app.services.zpt import ZPTTemplate
from zope.app.services.view import ViewService
from zope.app.interfaces.services.registration import ActiveStatus
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.services.tests.test_registrationmanager \
     import RegistrationManagerContainerTests
from zope.component.adapter import provideAdapter

class I(Interface):
    pass

class I2(Interface):
    pass

class Test(RegistrationManagerContainerTests, PlacefulSetup, TestCase):

    def setUp(self):
        sm = PlacefulSetup.setUp(self, site=True)
        provideAdapter(IPageFolder, IZopeContextWrapper,
                       PageFolderContextDecorator)
        setup.addService(sm, 'Views', ViewService(), suffix='service')
        default = traverse(self.rootFolder, '++etc++site/default')
        default.setObject('Views', PageFolder())
        views = traverse(default, 'Views')
        views.forInterface = I
        views.factoryName = None
        views.permission = 'zope.View'

        self.__views = views

    def test_setObject(self):

        views = self.__views

        views.setObject('foo.html', ZPTTemplate())

        registration = traverse(views.getRegistrationManager(), '1')
        self.assertEqual(registration.status, ActiveStatus)
        self.assertEqual(registration.forInterface, I)
        self.assertEqual(registration.presentationType, IBrowserPresentation)
        self.assertEqual(registration.viewName, u'foo.html')
        self.assertEqual(registration.layer, 'default')
        self.assertEqual(registration.class_, None)
        self.assertEqual(registration.permission, 'zope.View')
        self.assertEqual(registration.attribute, None)

        self.assertRaises(TypeError,
                          views.setObject, 'bar.html', PageFolder())

    def test_applyDefaults(self):

        views = self.__views

        views.setObject('foo.html', ZPTTemplate())

        registration = traverse(views.getRegistrationManager(), '1')
        self.assertEqual(registration.status, ActiveStatus)
        self.assertEqual(registration.forInterface, I)
        self.assertEqual(registration.presentationType, IBrowserPresentation)
        self.assertEqual(registration.viewName, u'foo.html')
        self.assertEqual(registration.layer, 'default')
        self.assertEqual(registration.class_, None)
        self.assertEqual(registration.permission, 'zope.View')
        self.assertEqual(registration.attribute, None)

        views.forInterface = I2
        views.permission = 'zope.ManageContent'
        views.layer = 'debug'
    
        views.applyDefaults()

        registration = traverse(views.getRegistrationManager(), '1')
        self.assertEqual(registration.status, ActiveStatus)
        self.assertEqual(registration.forInterface, I2)
        self.assertEqual(registration.presentationType, IBrowserPresentation)
        self.assertEqual(registration.viewName, u'foo.html')
        self.assertEqual(registration.layer, 'debug')
        self.assertEqual(registration.class_, None)
        self.assertEqual(registration.permission, 'zope.ManageContent')
        self.assertEqual(registration.attribute, None)

        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

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

$Id: test_pagefolder.py,v 1.5 2003/06/05 12:03:18 stevea Exp $
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
from zope.app.interfaces.services.configuration import Active
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.services.tests.test_configurationmanager \
     import ConfigurationManagerContainerTests
from zope.component.adapter import provideAdapter

class I(Interface):
    pass

class Test(ConfigurationManagerContainerTests, PlacefulSetup, TestCase):

    def test_setObject(self):
        provideAdapter(IPageFolder, IZopeContextWrapper,
                       PageFolderContextDecorator)
        sm = self.buildFolders(site=True)
        setup.addService(sm, 'Views', ViewService(), suffix='service')

        default = traverse(self.rootFolder, '++etc++site/default')
        default.setObject('Views', PageFolder())
        views = traverse(default, 'Views')
        views.forInterface = I
        views.factoryName = None
        views.permission = 'zope.View'
        views.setObject('foo.html', ZPTTemplate())

        configuration = traverse(views.getConfigurationManager(), '1')
        self.assertEqual(configuration.status, Active)
        self.assertEqual(configuration.forInterface, I)
        self.assertEqual(configuration.presentationType, IBrowserPresentation)
        self.assertEqual(configuration.viewName, u'foo.html')
        self.assertEqual(configuration.layer, 'default')
        self.assertEqual(configuration.class_, None)
        self.assertEqual(configuration.permission, 'zope.View')
        self.assertEqual(configuration.attribute, None)

        self.assertRaises(TypeError,
                          views.setObject, 'bar.html', PageFolder())


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

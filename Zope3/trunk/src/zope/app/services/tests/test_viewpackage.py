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

$Id: test_viewpackage.py,v 1.6 2003/03/18 21:02:23 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.viewpackage import ViewPackage
from zope.app.traversing import traverse
from zope.app.services.zpt import ZPTTemplate
from zope.app.services.view import ViewService
from zope.app.interfaces.services.configuration import Active
from zope.app.services.service import ServiceManager
from zope.app.services.service import ServiceConfiguration
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserPresentation

class I(Interface): pass

class Test(PlacefulSetup, TestCase):

    def test_setObject(self):
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        default = traverse(self.rootFolder, '++etc++Services/default')
        default.setObject('Views', ViewPackage())
        views = traverse(default, 'Views')
        views.forInterface = I
        views.factoryName = None
        views.permission = 'zope.View'

        #set up view service
        default.setObject('ViewService', ViewService())
        configure = traverse(default, 'configure')
        configuration = ServiceConfiguration(
            'Views',
            '/++etc++Services/default/ViewService')
        configure.setObject('', configuration)
        configuration = traverse(configure, '1')
        configuration.status = Active

        views.setObject('foo.html', ZPTTemplate())

        configuration = traverse(views, 'configure/1')
        self.assertEqual(configuration.status, Active)
        self.assertEqual(configuration.forInterface, I)
        self.assertEqual(configuration.presentationType, IBrowserPresentation)
        self.assertEqual(configuration.viewName, u'foo.html')
        self.assertEqual(configuration.layer, 'default')
        self.assertEqual(configuration.class_, None)
        self.assertEqual(configuration.permission, 'zope.View')
        self.assertEqual(configuration.attribute, None)

        self.assertRaises(TypeError,
                          views.setObject, 'bar.html', ViewPackage())


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

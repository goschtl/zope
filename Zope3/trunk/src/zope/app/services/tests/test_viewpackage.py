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

$Id: test_viewpackage.py,v 1.3 2003/02/03 17:29:11 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup \
     import PlacefulSetup
from zope.app.services.viewpackage import ViewPackage
from zope.app.traversing import traverse
from zope.app.services.zpt import ZPTTemplate
from zope.app.services.view import ViewService
from zope.app.interfaces.services.configuration import Active
from zope.app.services.service import ServiceManager
from zope.app.services.service \
     import ServiceConfiguration
from zope.interface import Interface

class Test(PlacefulSetup, TestCase):

    def test_setObject(self):
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        default = traverse(self.rootFolder, '++etc++Services/Packages/default')
        default.setObject('Views', ViewPackage())
        views = traverse(default, 'Views')
        views.forInterface = Interface
        views.factoryName = None
        views.permission = None

        #set up view service
        default.setObject('ViewService', ViewService())
        configure = traverse(default, 'configure')
        configuration = ServiceConfiguration(
            'Views',
            '/++etc++Services/Packages/default/ViewService')
        configure.setObject('', configuration)
        configuration = traverse(configure, '1')
        configuration.status = Active

        views.setObject('foo.html', ZPTTemplate())

        configuration = traverse(views, 'configure/1')
        self.assertEqual(configuration.status, Active)

        self.assertRaises(TypeError,
                          views.setObject, 'bar.html', ViewPackage())


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

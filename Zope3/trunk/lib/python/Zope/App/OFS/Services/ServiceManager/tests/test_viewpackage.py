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

$Id: test_viewpackage.py,v 1.2 2002/12/19 20:38:26 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.App.OFS.Services.ServiceManager.viewpackage import ViewPackage
from Zope.App.Traversing import traverse
from Zope.App.OFS.Services.zpt import ZPTTemplate
from Zope.App.OFS.Services.view import ViewService
from Zope.App.OFS.Services.ConfigurationInterfaces import Active
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Interface import Interface

class Test(PlacefulSetup, TestCase):

    def test_setObject(self):
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        default = traverse(self.rootFolder, '++etc++Services/Packages/default')
        default.setObject('Views', ViewPackage())
        views = traverse(default, 'Views')
        views.forInterface = Interface
        views.factoryName = None

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

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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testServiceConfigURL.py,v 1.2 2002/11/30 18:39:17 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Zope.App.Traversing import traverse
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Services.ServiceManager.Browser.ServiceConfigURL \
     import ServiceConfigURL
from Zope.Publisher.Browser.BrowserRequest import TestRequest

class V(BrowserView, ServiceConfigURL):
    pass

class C:
    pass



class Test(PlacefulSetup, TestCase):

    def test(self):
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        default = traverse(
            self.rootFolder,
            '++etc++Services/Packages/default',
            )
        default.setObject('c', C())
        traverse(default, 'configure').setObject(
            '',
            ServiceConfiguration('test_service',
                                 '/++etc++Services/Packages/default/c')
            )
        config = traverse(default, 'configure/1')
        view = V(config, TestRequest())
        self.assertEqual(view.componentURL(),
                         'http://127.0.0.1/++etc++Services/Packages/default/c')
        
        
        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

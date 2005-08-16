##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Page folder tests.

$Id$
"""
import unittest
import zope.interface
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.app import zapi
from zope.app.component.interfaces.registration import ActiveStatus
from zope.app.component.testing import PlacefulSetup
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.presentation.interfaces import IPageFolder, IZPTTemplate
from zope.app.presentation.pagefolder import PageFolder
from zope.app.presentation.pagefolder import templateAddedSubscriber
from zope.app.presentation.zpt import ZPTTemplate
from zope.app.testing import ztapi, setup

class I(zope.interface.Interface):
    pass

class I2(zope.interface.Interface):
    pass

class PageFolderTest(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        sm = PlacefulSetup.setUp(self, site=True)
        default = zapi.traverse(self.rootFolder, '++etc++site/default')
        setup.setUpAnnotations()
        setup.setUpTraversal()
        ztapi.subscribe((IZPTTemplate, IObjectAddedEvent),
                        None, templateAddedSubscriber)

        default["PF"] = PageFolder()
        pagefolder = zapi.traverse(default, "PF")

        pagefolder.required = I
        pagefolder.factoryName = None
        pagefolder.permission = 'zope.View'

        self.__pagefolder = pagefolder

    def test_templateAddedSubscriber(self):
        
        pagefolder = self.__pagefolder

        pagefolder['foo.html'] = ZPTTemplate()

        rm = pagefolder.registrationManager
        name = rm.keys()[0]
        registration = zapi.traverse(rm, name)
        self.assertEqual(registration.status, ActiveStatus)
        self.assertEqual(registration.required, I)
        self.assertEqual(registration.requestType, IBrowserRequest)
        self.assertEqual(registration.name, u'foo.html')
        self.assertEqual(registration.factoryName, None)
        self.assertEqual(registration.permission, 'zope.View')
        self.assertEqual(registration.attribute, None)

    def test_applyDefaults(self):

        pagefolder = self.__pagefolder

        pagefolder['foo.html'] = ZPTTemplate()

        rm = pagefolder.registrationManager
        name = rm.keys()[-1]
        registration = zapi.traverse(rm, name)
        self.assertEqual(registration.status, ActiveStatus)
        self.assertEqual(registration.required, I)
        self.assertEqual(registration.requestType, IBrowserRequest)
        self.assertEqual(registration.name, u'foo.html')
        self.assertEqual(registration.factoryName, None)
        self.assertEqual(registration.permission, 'zope.View')
        self.assertEqual(registration.attribute, None)

        pagefolder.required = I2
        pagefolder.permission = 'zope.ManageContent'

        pagefolder.applyDefaults()

        registration = zapi.traverse(rm, name)
        self.assertEqual(registration.status, ActiveStatus)
        self.assertEqual(registration.required, I2)
        self.assertEqual(registration.requestType, IBrowserRequest)
        self.assertEqual(registration.name, u'foo.html')
        self.assertEqual(registration.factoryName, None)
        self.assertEqual(registration.permission, 'zope.ManageContent')
        self.assertEqual(registration.attribute, None)

        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PageFolderTest),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

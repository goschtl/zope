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
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.tests import ztapi
from zope.app.tests import setup
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.presentation.pagefolder import PageFolder, IPageFolder
from zope.app.presentation.zpt import ZPTTemplate
from zope.app.presentation import LocalPresentationService
from zope.app.registration.interfaces import ActiveStatus
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.registration.tests.test_registrationmanager \
     import RegisterableContainerTests
from zope.component.servicenames import Presentation

from zope.app.dependable.interfaces import IDependable
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.dependable import Dependable
from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotations, IAnnotatable
from zope.app.annotation.attribute import AttributeAnnotations



class I(Interface):
    pass

class I2(Interface):
    pass

class Test(RegisterableContainerTests, PlacefulSetup, TestCase):

    def setUp(self):
        sm = PlacefulSetup.setUp(self, site=True)
        zapi.getGlobalService(Presentation).defineLayer('debug')
        setup.addService(sm, Presentation, LocalPresentationService(),
                         suffix='service')
        default = zapi.traverse(self.rootFolder, '++etc++site/default')

        ztapi.provideAdapter(IAnnotatable, IAnnotations,
                         AttributeAnnotations)

        ztapi.provideAdapter(IAnnotatable, IDependable,
                         Dependable)

        default["PF"] = PageFolder()
        pagefolder = zapi.traverse(default, "PF")

        pagefolder.required = I
        pagefolder.factoryName = None
        pagefolder.permission = 'zope.View'

        self.__pagefolder = pagefolder



    def test___setitem__(self):
        
        pagefolder = self.__pagefolder

        pagefolder['foo.html'] = ZPTTemplate()

        rm = pagefolder.getRegistrationManager()
        name = rm.keys()[-1]
        registration = zapi.traverse(pagefolder.getRegistrationManager(),
                                     name)
        self.assertEqual(registration.status, ActiveStatus)
        self.assertEqual(registration.required, I)
        self.assertEqual(registration.requestType, IBrowserRequest)
        self.assertEqual(registration.name, u'foo.html')
        self.assertEqual(registration.layer, 'default')
        self.assertEqual(registration.factoryName, None)
        self.assertEqual(registration.permission, 'zope.View')
        self.assertEqual(registration.attribute, None)

        self.assertRaises(TypeError,
                          pagefolder.__setitem__, 'bar.html', PageFolder())

    def test_applyDefaults(self):

        pagefolder = self.__pagefolder

        pagefolder['foo.html'] = ZPTTemplate()

        rm = pagefolder.getRegistrationManager()
        name = rm.keys()[-1]
        registration = zapi.traverse(pagefolder.getRegistrationManager(), name)
        self.assertEqual(registration.status, ActiveStatus)
        self.assertEqual(registration.required, I)
        self.assertEqual(registration.requestType, IBrowserRequest)
        self.assertEqual(registration.name, u'foo.html')
        self.assertEqual(registration.layer, 'default')
        self.assertEqual(registration.factoryName, None)
        self.assertEqual(registration.permission, 'zope.View')
        self.assertEqual(registration.attribute, None)

        pagefolder.required = I2
        pagefolder.permission = 'zope.ManageContent'
        pagefolder.layer = 'debug'

        pagefolder.applyDefaults()

        registration = zapi.traverse(pagefolder.getRegistrationManager(), name)
        self.assertEqual(registration.status, ActiveStatus)
        self.assertEqual(registration.required, I2)
        self.assertEqual(registration.requestType, IBrowserRequest)
        self.assertEqual(registration.name, u'foo.html')
        self.assertEqual(registration.layer, 'debug')
        self.assertEqual(registration.factoryName, None)
        self.assertEqual(registration.permission, 'zope.ManageContent')
        self.assertEqual(registration.attribute, None)

        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

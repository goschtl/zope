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
import unittest, sys
from Interface import Interface

from Zope.ComponentArchitecture import getService
from Zope.App.ZMI.ZMIViewService import ZMIViewService
from Zope.App.ZMI.tests.sampleInterfaces import *
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup\
           import PlacefulSetup



class Test(PlacefulSetup, unittest.TestCase):
    #XXX we should have a test for multiple inheritance interface
    # hierarchies.

    def testAddView(self):

        getService(None,"Adapters").provideAdapter(
            I1, ITraverser, FakeTraverser)
        getService(None,"Adapters").provideAdapter(
            I2, ITraverser, FakeTraverser)

        service = ZMIViewService()
        service.registerView(I1, 'Edit', 'edit')
        service.registerView(I1, 'History', 'history')
        service.registerView(I2, 'Update', 'update_magic')
        service.registerView(I2, 'Organize', 'organize_magic')

        self.assertEqual(list(service.getViews(O1())),
                         [('Edit', 'edit'), ('History', 'history')])

        self.assertEqual(list(service.getViews(O2())),
                         [
                          ('Update', 'update_magic'),
                          ('Organize', 'organize_magic'),
                          ('Edit', 'edit'),
                          ('History', 'history')
                          ]
                         )

    def testZMIFilter(self):

        getService(None,"Adapters").provideAdapter(
            I1, ITraverser, FakeTraverser)
        getService(None,"Adapters").provideAdapter(
            I2, ITraverser, FakeTraverser)

        service = ZMIViewService()
        service.registerView(I1, 'Edit', 'edit', 'python: 2==2')
        service.registerView(I1, 'History', 'history', 'python: 1==2')
        service.registerView(I2, 'Update', 'update_magic', 'python: 2==2')
        service.registerView(I2, 'Organize', 'organize_magic', 'python: 1==2')

        self.assertEqual(list(service.getViews(O1())),
                         [('Edit', 'edit'),])

        self.assertEqual(list(service.getViews(O2())),
                         [('Update', 'update_magic'), ('Edit', 'edit')]
                         )


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())


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
"""

$Id: testAddable.py,v 1.2 2002/06/10 23:28:10 jim Exp $
"""

import unittest, sys
from Zope.ComponentArchitecture import getService
from Zope.App.OFS.Services.AddableService.Addable import Addable
from Zope.App.OFS.Services.AddableService import getAddableContent, \
     getAddableServices
from AddableSetup import AddableSetup

def membership_check(group, item):
    if type(group) is tuple:
        for inter in group:
            if membership_check(inter, item):
                return 1
        return 0
    if type(item) is tuple:
        for inter in item:
            if membership_check(group, inter):
                return 1
        return 0
    return group is item or issubclass(item, group)

class Test(AddableSetup, unittest.TestCase):

    def testService(self):

        self.assertEqual(getAddableContent(None), [])

        getService(None, 'AddableContent').provideAddable(
            'Contact', 'Personal Contact',
            'blah\nblah')

        # you must provide a matching factory for the addable to be returned
        self.assertEqual(getAddableContent(None), [])

        from Interface import Interface
        class IA(Interface):
            pass
        class A:
            __implements__=IA
        from Zope.ComponentArchitecture.tests.TestFactory import ClassFactoryWrapper
        fA=ClassFactoryWrapper(A)
        getService(None, 'Factories').provideFactory('Contact', fA)

        self.assertEqual(getAddableContent(None), [
            Addable('Contact', 'Personal Contact', 'blah\nblah'),
            ])

        getService(None, 'Factories').provideFactory('spam', fA)
        getService(None,'AddableContent').provideAddable('spam', 'junk mail', 'spam\nspam')

        self.assertEqual(getAddableContent(None), [
            Addable('Contact', 'Personal Contact', 'blah\nblah'),
            Addable('spam', 'junk mail', 'spam\nspam'),
            ]) # ought to change to some kind of sort for more robust check
    
    def testGetAddable(self):
        self.buildFolders()
        from Interface import Interface

        # objects

        class IA(Interface):
            pass
        class A:
            __implements__=IA
        class IB(Interface):
            pass
        class B:
            __implements__=IB
        class IBC(IB):
            pass
        class C:
            __implements__=IBC
        class D:
            __implements__=(IA, (IBC,))
        class E:
            __implements__=IA

        # factories
        from Zope.ComponentArchitecture.tests.TestFactory import ClassFactoryWrapper

        fA=ClassFactoryWrapper(A)
        fB=ClassFactoryWrapper(B)
        fC=ClassFactoryWrapper(C)
        fD=ClassFactoryWrapper(D)
        fE=ClassFactoryWrapper(E)

        #containers

        class IX(Interface):
            pass
        class IX1(Interface):
            pass
        self.folder1.__implements__+= (IX, IX1)
        class IY(IX):
            pass
        self.folder1_1.__implements__+= (IY,)
        # (the fancy one...)
        class IZ(Interface):
            pass
        from Zope.App.OFS.Content.Folder.Folder import Folder
        from Zope.ContextWrapper import Wrapper
        from Zope.App.OFS.Container.IContainer import IHomogenousContainer

        class DummyFolder(Folder):
            __implements__=Folder.__implements__, IZ, IHomogenousContainer

            def isAddable(self, interfaces):
                return membership_check(IB, interfaces)


        self.folder3=DummyFolder()
        self.rootFolder.setObject("folder3",self.folder3)
        self.folder3=Wrapper(self.folder3, self.rootFolder, name="folder3")
        
        # set up the services with the factories and addables...
        provideFactory=getService(None, 'Factories').provideFactory
        provideAddable=getService(None, 'AddableServices').provideAddable
        provideFactory('A', fA)

        # should be available in 1 and 1_1 (for_container)
        provideAddable('A', 'Dummy A', 'Desc A', IX)
        provideFactory('B', fB)

        # should be in 1 and 3 (for_container)
        provideAddable('B', 'Dummy B', 'Desc B', (IX1, IZ))
        provideFactory('C', fC)

        # should be in 1 (for_container)
        provideAddable('C', 'DummyC', 'Desc C', IX1)
        provideFactory('D', fD)

        # should be in ALLOW
        provideAddable('D', 'Dummy D', 'Desc D')
        provideFactory('E', fE)

        # should be in 1 and 1_1
        provideAddable('E', 'Dummy E', 'Desc E')
        AAd=Addable('A', 'Dummy A', 'Desc A', IX)
        BAd=Addable('B', 'Dummy B', 'Desc B', (IX1, IZ))
        CAd=Addable('C', 'DummyC', 'Desc C', IX1)
        DAd=Addable('D', 'Dummy D', 'Desc D')
        EAd=Addable('E', 'Dummy E', 'Desc E')
        
        # and test!

        # sort for more robust test
        self.assertEqual(getAddableServices(self.folder1),
                         [AAd, BAd, CAd, DAd, EAd])
        self.assertEqual(getAddableServices(self.folder1_1),
                         [AAd, DAd, EAd]) # sort
        self.assertEqual(getAddableServices(self.folder3),
                         [BAd, DAd]) # sort
        
        
    def setAValue(self, add,val):
        add.id=val
    
    def testAddable(self):
        myAddable=Addable('Contact', 'Personal Contact',
                                        'blah\nblah')
        self.assertRaises(AttributeError,
                          self.setAValue, myAddable, 'AnotherId')

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

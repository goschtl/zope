##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Browser Menu Service Tests

$Id$
"""
import unittest

from zope.app import zapi
from interfaces import ILocalBrowserMenuService, ILocalBrowserMenu
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.publisher.interfaces.browser import IBrowserMenuService
from zope.app.registration.interfaces import ActiveStatus
from zope.app.utility.interfaces import ILocalUtility
from zope.app.publisher.browser.globalbrowsermenuservice import \
     globalBrowserMenuService
from zope.app.menu import \
     LocalBrowserMenuService, LocalBrowserMenu, LocalBrowserMenuItem
from zope.app.utility import LocalUtilityService, UtilityRegistration
from zope.app.servicenames import BrowserMenu, Utilities
from zope.app.tests import setup
from zope.component import getGlobalServices
from zope.component.exceptions import ComponentLookupError
from zope.interface import Interface, implements, classImplements
from zope.publisher.browser import TestRequest

class I1(Interface): pass
class I12(I1): pass
class I11(I1): pass

class TestObject(object):
    implements(IBrowserPublisher, I11)

    def f(self):
        pass

    def browserDefault(self, r):
        return self, ()

    def publishTraverse(self, request, name):
        if name[:1] == 'f':
            raise Forbidden, name
        if name[:1] == 'u':
            raise Unauthorized, name
        return self.f


def addMenu(servicemanager, menu_id, title, inherit):
    """Add a menu to the service manager's default package."""
    menu = LocalBrowserMenu()
    menu.title = title
    menu.inherit = inherit

    default = zapi.traverse(servicemanager, 'default')
    default[menu_id] = menu
    path = "%s/default/%s" % (zapi.getPath(servicemanager), menu_id)
    registration = UtilityRegistration(menu_id, ILocalBrowserMenu, path)
    key = default.getRegistrationManager().addRegistration(registration)
    zapi.traverse(default.getRegistrationManager(), key).status = ActiveStatus
    return zapi.traverse(default, menu_id)


def addMenuItem(menu, interface, action, title):
    item = LocalBrowserMenuItem()
    item.title = title
    item.action = action
    item.interface = interface
    menu.addItem(item)
    return item


class LocalBrowserMenuServiceTest(unittest.TestCase):
    """Test Interface for LocalInterfaceService instance."""

    def setUp(self):
        setup.placefulSetUp()
        self.rootFolder = setup.buildSampleFolderTree()

        # Define Menu Service
        sm = getGlobalServices()
        sm.defineService(BrowserMenu, IBrowserMenuService)
        sm.provideService(BrowserMenu, globalBrowserMenuService)
        classImplements(LocalBrowserMenu, ILocalUtility)
        classImplements(LocalBrowserMenu, IAttributeAnnotatable)
        
        # Create Placeless Components
        ps = zapi.getGlobalService(zapi.servicenames.Presentation)
        ms = zapi.getGlobalService(BrowserMenu)
        ms.menu('test_id', 'test menu')
        ms.menu('test_id2', 'test menu 2')
        ms.menu('test_id3', 'test menu 3')
        ms.menuItem('test_id', Interface, 'a0', 't0', 'd0')
        ms.menuItem('test_id',   I1, 'a1', 't1', 'd1')
        ms.menuItem('test_id',  I11, 'a2', 't2', 'd2')
        ms.menuItem('test_id',  I12, 'a3', 't3', 'd3')
        ms.menuItem('test_id2',  I1, 'a4', 't4', 'd4')
        ms.menuItem('test_id2', I11, 'a5', 't5', 'd5')
        ms.menuItem('test_id2', I12, 'a6', 't6', 'd6')
        ms.menuItem('test_id3',  I1, 'a7', 't7', 'd7')
        ms.menuItem('test_id3', I11, 'a8', 't8', 'd8')
        ms.menuItem('test_id3', I12, 'a9', 't9', 'd9')

        # Create Components in root folder
        mgr = setup.createServiceManager(self.rootFolder)
        setup.addService(mgr, Utilities, LocalUtilityService())
        self.root_ms = setup.addService(mgr, BrowserMenu,
                                        LocalBrowserMenuService())
        menu = addMenu(mgr, 'test_id', 'test menu r', True)
        addMenuItem(menu, I1,  'ar1', 'tr1')
        addMenuItem(menu, I11, 'ar2', 'tr2')
        addMenuItem(menu, I12, 'ar3', 'tr3')
        menu = addMenu(mgr, 'test_id2', 'test menu 2 r', False)
        addMenuItem(menu, I1,  'ar4', 'tr4')
        addMenuItem(menu, I11, 'ar5', 'tr5')
        addMenuItem(menu, I12, 'ar6', 'tr6')
        
        # Create Components in folder1
        folder1 = zapi.traverse(self.rootFolder, 'folder1')
        mgr = setup.createServiceManager(folder1)
        setup.addService(mgr, Utilities, LocalUtilityService())
        self.folder_ms = setup.addService(mgr, BrowserMenu,
                                          LocalBrowserMenuService())
        menu = addMenu(mgr, 'test_id', 'test menu f', True)
        addMenuItem(menu, I1,  'af1', 'tf1')
        addMenuItem(menu, I11, 'af2', 'tf2')
        addMenuItem(menu, I12, 'af3', 'tf3')
        menu = addMenu(mgr, 'test_id3', 'test menu 3 f', True)
        addMenuItem(menu, I1,  'af7', 'tf7')
        addMenuItem(menu, I11, 'af8', 'tf8')
        addMenuItem(menu, I12, 'af9', 'tf9')

        
    def tearDown(self):
        setup.placefulTearDown()


    def test_VerifyInterfaceImplementation(self):
        self.assert_(ILocalBrowserMenuService.providedBy(
            LocalBrowserMenuService()))


    def test_getAllLocalMenus(self):
        menus = self.root_ms.getAllLocalMenus()
        titles = map(lambda m: m.title, menus)
        titles.sort()
        self.assertEqual(titles, ['test menu 2 r', 'test menu r'])

        menus = self.folder_ms.getAllLocalMenus()
        titles = map(lambda m: m.title, menus)
        titles.sort()
        self.assertEqual(titles, ['test menu 3 f', 'test menu f'])


    def test_queryLocalMenu(self):
        for ms, menu_id, title in [
            (self.root_ms, 'test_id', 'test menu r'),
            (self.root_ms, 'test_id2', 'test menu 2 r'),
            (self.folder_ms, 'test_id', 'test menu f'),
            (self.folder_ms, 'test_id3', 'test menu 3 f'),
            ]:
            self.assertEqual(ms.queryLocalMenu(menu_id).title, title)

        self.assertEqual(self.root_ms.queryLocalMenu('test_id3'), None)
        self.assertEqual(self.folder_ms.queryLocalMenu('test_id2'), None)


    def test_getLocalMenu(self):
        for ms, menu_id, title in [
            (self.root_ms, 'test_id', 'test menu r'),
            (self.root_ms, 'test_id2', 'test menu 2 r'),
            (self.folder_ms, 'test_id', 'test menu f'),
            (self.folder_ms, 'test_id3', 'test menu 3 f'),
            ]:
            self.assertEqual(ms.getLocalMenu(menu_id).title, title)

        self.assertRaises(ComponentLookupError, self.root_ms.getLocalMenu,
                          'test_id3')
        self.assertRaises(ComponentLookupError, self.folder_ms.getLocalMenu,
                          'test_id2')


    def test_queryInheritedMenu(self):
        for ms, menu_id, canBeLocal, title in [
            (self.root_ms, 'test_id', True, 'test menu r'),
            (self.root_ms, 'test_id', False, 'test menu'),
            (self.root_ms, 'test_id3', True, 'test menu 3'),
            (self.root_ms, 'test_id3', False, 'test menu 3'),
            (self.folder_ms, 'test_id', True, 'test menu f'),
            (self.folder_ms, 'test_id', False, 'test menu r'),
            (self.folder_ms, 'test_id2', True, 'test menu 2 r'),
            (self.folder_ms, 'test_id2', False, 'test menu 2 r'),
            (self.folder_ms, 'test_id3', True, 'test menu 3 f'),
            (self.folder_ms, 'test_id3', False, 'test menu 3'),
            ]:
            self.assertEqual(
                ms.queryInheritedMenu(menu_id, canBeLocal).title, title)

        self.assertEqual(self.root_ms.queryInheritedMenu('test_id4'), None)
        self.assertEqual(self.folder_ms.queryInheritedMenu('test_id4'), None)


    def test_getInheritedMenu(self):
        for ms, menu_id, canBeLocal, title in [
            (self.root_ms, 'test_id', True, 'test menu r'),
            (self.root_ms, 'test_id', False, 'test menu'),
            (self.root_ms, 'test_id3', True, 'test menu 3'),
            (self.root_ms, 'test_id3', False, 'test menu 3'),
            (self.folder_ms, 'test_id', True, 'test menu f'),
            (self.folder_ms, 'test_id', False, 'test menu r'),
            (self.folder_ms, 'test_id2', True, 'test menu 2 r'),
            (self.folder_ms, 'test_id2', False, 'test menu 2 r'),
            (self.folder_ms, 'test_id3', True, 'test menu 3 f'),
            (self.folder_ms, 'test_id3', False, 'test menu 3'),
            ]:
            self.assertEqual(
                ms.getInheritedMenu(menu_id, canBeLocal).title, title)

        self.assertRaises(ComponentLookupError,
                          self.root_ms.getInheritedMenu, 'test_id4')
        self.assertRaises(ComponentLookupError,
                          self.root_ms.getInheritedMenu, 'test_id4', True)
        self.assertRaises(ComponentLookupError,
                          self.folder_ms.getInheritedMenu, 'test_id4')


    def test_getAllMenuItems(self):
        for ms, menu_id, titles in [
            (self.root_ms, 'test_id', ('a0', 'a1', 'a2', 'ar1', 'ar2')),
            (self.root_ms, 'test_id2', ('ar4', 'ar5')),
            (self.root_ms, 'test_id3', ('a7', 'a8')),
            (self.folder_ms, 'test_id', ('a0', 'a1', 'a2', 'af1', 'af2',
                                         'ar1', 'ar2')),
            (self.folder_ms, 'test_id2', ('ar4', 'ar5')),
            (self.folder_ms, 'test_id3', ('a7', 'a8', 'af7', 'af8')),
            ]:
            actions = map(lambda m: m.action,
                          ms.getAllMenuItems(menu_id, TestObject()))
            actions.sort()
            self.assertEqual(tuple(actions), titles)

        self.assertRaises(KeyError, self.folder_ms.getAllMenuItems, 'test_id4',
                          TestObject())
        self.assertRaises(KeyError, self.root_ms.getAllMenuItems, 'test_id4',
                          TestObject())

        actions = map(lambda m: m.action,
                      self.folder_ms.getAllMenuItems('test_id', None))
        actions.sort()
        self.assertEqual(tuple(actions), ('a0', 'a1', 'a2', 'a3',
                                          'af1', 'af2', 'af3',
                                          'ar1', 'ar2', 'ar3'))

    def test_getMenu(self):
        for ms, menu_id, titles in [
            (self.root_ms, 'test_id', ('a0', 'a1', 'a2', 'ar1', 'ar2')),
            (self.root_ms, 'test_id2', ('ar4', 'ar5')),
            (self.root_ms, 'test_id3', ('a7', 'a8')),
            (self.folder_ms, 'test_id', ('a0', 'a1', 'a2', 'af1', 'af2',
                                         'ar1', 'ar2')),
            (self.folder_ms, 'test_id2', ('ar4', 'ar5')),
            (self.folder_ms, 'test_id3', ('a7', 'a8', 'af7', 'af8')),
            ]:
            actions = map(lambda m: m['action'],
                          ms.getMenu(menu_id, TestObject(), TestRequest()))
            actions.sort()
            self.assertEqual(tuple(actions), titles)

        self.assertRaises(KeyError, self.root_ms.getMenu, 'test_id4',
                          TestObject(), TestRequest())
        self.assertRaises(KeyError, self.folder_ms.getMenu, 'test_id4',
                          TestObject(), TestRequest())
        self.assertRaises(KeyError, self.folder_ms.getMenu,
                          'test_id', None, TestRequest())


    def test_getFirstMenuItem(self):
        for ms, menu_id, action in [
            (self.root_ms, 'test_id', 'ar1'),
            (self.root_ms, 'test_id2', 'ar4'),
            (self.root_ms, 'test_id3', 'a8'),
            (self.folder_ms, 'test_id', 'af1'),
            (self.folder_ms, 'test_id2', 'ar4'),
            (self.folder_ms, 'test_id3', 'af7'),
            ]:
            item = ms.getFirstMenuItem(menu_id, TestObject(), TestRequest())
            self.assertEqual(item['action'], action)

        self.assertRaises(KeyError, self.root_ms.getFirstMenuItem,
                          'test_id4', TestObject(), TestRequest())
        self.assertRaises(KeyError, self.folder_ms.getFirstMenuItem,
                          'test_id4', TestObject(), TestRequest())

        self.assertRaises(KeyError, self.folder_ms.getFirstMenuItem,
                          'test_id', None, TestRequest())
       
        

def test_suite():
    return unittest.makeSuite(LocalBrowserMenuServiceTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

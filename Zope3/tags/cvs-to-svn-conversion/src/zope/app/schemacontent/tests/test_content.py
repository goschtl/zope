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
"""Content Component Definition and Instance Tests

$Id: test_content.py,v 1.5 2004/03/13 23:55:22 srichter Exp $
"""
import unittest

from zope.app import zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.container.interfaces import IAdding
from zope.app.publisher.interfaces.browser import IBrowserMenuService
from zope.app.utility.interfaces import ILocalUtility
from zope.app.schemacontent.interfaces import \
     IContentComponentDefinition, IContentComponentMenuItem
from zope.app.publisher.browser.globalbrowsermenuservice import \
     GlobalBrowserMenuService
from zope.app.menu import LocalBrowserMenuService, LocalBrowserMenu
from zope.app.menu.tests import addMenu
from zope.app.servicenames import BrowserMenu, Utilities
from zope.app.utility import LocalUtilityService
from zope.app.tests import setup
from zope.app.schemacontent.content import \
     ContentComponentDefinition, ContentComponentDefinitionRegistration, \
     ContentComponentDefinitionMenuItem, ContentComponentInstance
from zope.component import getServiceManager
from zope.app.tests import ztapi
from zope.component.exceptions import ComponentLookupError
from zope.interface import Interface, classImplements
from zope.schema import Int, TextLine, Text

class IDocument(Interface):
    id = Int(title=u"id", default=0)
    title = TextLine(title=u"title", default=u'Title goes here.')
    description = Text(title=u"desription")


class ContentComponentDefinitionRegistrationTests(unittest.TestCase):

    __name__ = __parent__ = None
    
    def setUp(self):
        setup.placefulSetUp()
        self.rootFolder = setup.buildSampleFolderTree()

        # Define Menu Item Adapter
        ztapi.provideAdapter(IContentComponentDefinition,
                             IContentComponentMenuItem,
                             ContentComponentDefinitionMenuItem)

        # Define Menu Service
        sm=getServiceManager(None)
        sm.defineService(BrowserMenu, IBrowserMenuService)
        sm.provideService(BrowserMenu, GlobalBrowserMenuService())
        classImplements(LocalBrowserMenu, ILocalUtility)
        classImplements(LocalBrowserMenu, IAttributeAnnotatable)
        mgr = setup.createServiceManager(self.rootFolder)
        self.root_ms = setup.addService(mgr, BrowserMenu,
                                        LocalBrowserMenuService())

        # Setup Utility Service
        setup.addService(mgr, Utilities, LocalUtilityService())

        # Define a Menu
        addMenu(mgr, 'add_content', 'Add Content', True)

        # Setup Definition
        classImplements(ContentComponentDefinition, ILocalUtility)
        classImplements(ContentComponentDefinition, IAttributeAnnotatable)
        default = zapi.traverse(mgr, 'default')
        default['TestDoc'] = ContentComponentDefinition()

        # Setup Definition Registration
        path = "%s/default/%s" % (zapi.getPath(mgr), 'TestDoc')
        reg = ContentComponentDefinitionRegistration(
            'TestDoc', IContentComponentDefinition, path)
        key = default.getRegistrationManager().addRegistration(reg)
        self.reg = zapi.traverse(default.getRegistrationManager(), key)
        
    def tearDown(self):
        setup.placefulTearDown()

    def test_activated(self):
        self.reg.activated()
        self.assertEqual(self.reg.getComponent().name, 'TestDoc')
        service = zapi.getService(self.rootFolder, BrowserMenu)
        menu = service.getLocalMenu('add_content')
        self.assertEqual('TestDoc', menu['1'].title)
        mi = IContentComponentMenuItem(self.reg.getComponent())
        self.assert_(mi._menuItem != None)
        self.assertEqual(mi._menu, menu)

    def test_deactivated(self):
        self.test_activated()
        self.reg.deactivated()
        mi = IContentComponentMenuItem(self.reg.getComponent())
        self.assertEqual(mi._menuItem, None)
        self.assertEqual(mi._menu, None)
        self.assertEqual(self.reg.getComponent().name, None)


class ContentComponentDefinitionMenuItemTests(unittest.TestCase):

    def setUp(self):
        setup.placefulSetUp()
        classImplements(ContentComponentDefinition, ILocalUtility)
        classImplements(ContentComponentDefinition, IAttributeAnnotatable)
        ztapi.provideAdapter(IContentComponentDefinition,
                             IContentComponentMenuItem,
                             ContentComponentDefinitionMenuItem)
        
        sm=getServiceManager(None)
        sm.defineService(BrowserMenu, IBrowserMenuService)
        sm.provideService(BrowserMenu, GlobalBrowserMenuService())

        self.rootFolder = setup.buildSampleFolderTree()
        self.mgr = setup.createServiceManager(self.rootFolder)

        setup.addService(self.mgr, Utilities, LocalUtilityService())
        ccd = ContentComponentDefinition('TestDoc', IDocument)
        self.default = zapi.traverse(self.mgr, 'default')
        self.default['Document'] = ccd
        ccd = zapi.traverse(self.default, 'Document')
        
        self.mi = ContentComponentDefinitionMenuItem(ccd)

    def tearDown(self):
        setup.placefulTearDown()

    def test_interface(self):
        self.assertEqual(self.mi.interface, IAdding)
        self.mi.interface = Interface
        self.assertEqual(self.mi.interface, Interface)

    def test_action(self):
        self.assertEqual(self.mi.action, 'AddContentComponent/TestDoc')
        self.mi.context.name = 'Document'
        self.assertEqual(self.mi.action, 'AddContentComponent/Document')

    def test_title(self):
        self.assertEqual(self.mi.title, 'TestDoc')
        self.mi.title = 'Test Document'
        self.assertEqual(self.mi.title, 'Test Document')

    def test_description(self):
        self.assertEqual(self.mi.description, '')
        self.mi.description = 'Test Document Description'
        self.assertEqual(self.mi.description, 'Test Document Description')

    def test_permission(self):
        self.assertEqual(self.mi.permission, 'zope.ManageContent')
        self.mi.permission = 'zope.View'
        self.assertEqual(self.mi.permission, 'zope.View')

    def test_filter_string(self):
        self.assertEqual(self.mi.filter_string, '')
        self.mi.filter_string = 'not: context'
        self.assertEqual(self.mi.filter_string, 'not: context')

    def test_createMenuService(self):
        menus = self.mi._createMenuService()
        self.assertEqual(zapi.name(menus), 'Menus-1')
        self.assert_('Menus-1' in zapi.getParent(menus))

    def test_createMenu(self):
        menu = self.mi._createMenu()
        self.assertEqual(zapi.name(menu), 'add_content')
        self.assert_('add_content' in zapi.getParent(menu))

    def test_createMenuItem(self):
        self.mi.createMenuItem()
        self.assert_('Menus-1' in self.default)
        self.assert_('add_content' in self.default)
        menu = zapi.traverse(self.default, 'add_content')
        item = menu.values()[0]
        self.assertEqual(item.action, 'AddContentComponent/TestDoc')

    def test_create(self):
        # This tests also createMenuItem and removeMenuItem
        self.assertEqual(self.mi.create, True)
        self.mi.createMenuItem()
        self.assertRaises(ComponentLookupError, self.mi.__setattr__,
                          'create', False)
        self.mi._data['create'] = False
        self.assertEqual(self.mi.create, False)


class ContentComponentInstanceTests(unittest.TestCase):
    
    def test_getattr(self):
        doc = ContentComponentInstance('Document', IDocument)
        self.assertEqual(doc.id, 0)
        self.assertEqual(doc.title, 'Title goes here.')
        self.assertEqual(doc.description, None)
        self.assertRaises(AttributeError, getattr, doc, 'foo')

    def test_setattr(self):
        doc = ContentComponentInstance('Document', IDocument)
        doc.id = 1 
        self.assertEqual(doc.id, 1)
        doc.title = 'Doc 1'
        self.assertEqual(doc.title, 'Doc 1')
        doc.description = 'This is doc 1.'
        self.assertEqual(doc.description, 'This is doc 1.')
        self.assertRaises(AttributeError, setattr, doc, 'foo', 'bar')
        
    def test_getSchema(self):
        doc = ContentComponentInstance('Document', IDocument)
        self.assertEqual(doc.getSchema(), IDocument)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ContentComponentDefinitionRegistrationTests),
        unittest.makeSuite(ContentComponentDefinitionMenuItemTests),
        unittest.makeSuite(ContentComponentInstanceTests),
        ))

if __name__ == '__main__':
    unittest.main()

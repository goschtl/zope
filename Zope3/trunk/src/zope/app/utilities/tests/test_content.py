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

$Id: test_content.py,v 1.2 2003/08/16 00:44:27 srichter Exp $
"""
import unittest

from zope.app import zapi
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.publisher.browser import IBrowserMenuService
from zope.app.interfaces.services.utility import ILocalUtility
from zope.app.interfaces.utilities.content import IContentComponentDefinition
from zope.app.services.menu import LocalBrowserMenuService, LocalBrowserMenu
from zope.app.services.tests.test_menu import addMenu
from zope.app.services.servicenames import BrowserMenu, Utilities
from zope.app.services.utility import LocalUtilityService
from zope.app.tests import setup
from zope.app.utilities.content import \
     ContentComponentDefinition, ContentComponentDefinitionRegistration
from zope.app.utilities.content import ContentComponentInstance
from zope.component import getServiceManager
from zope.interface import Interface, classImplements
from zope.schema import Int, TextLine, Text

class IDocument(Interface):
    id = Int(title=u"id", default=0)
    title = TextLine(title=u"title", default=u'Title goes here.')
    description = Text(title=u"desription")


class ContentComponentDefinitionRegistrationTests(unittest.TestCase):

    def setUp(self):
        setup.placefulSetUp()
        self.rootFolder = setup.buildSampleFolderTree()

        # Define Menu Service
        sm=getServiceManager(None)
        sm.defineService(BrowserMenu, IBrowserMenuService)
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
        default.setObject('TestDoc', ContentComponentDefinition())

        # Setup Definition Registration
        path = "%s/default/%s" % (zapi.getPath(mgr), 'TestDoc')
        reg = ContentComponentDefinitionRegistration(
            'TestDoc', IContentComponentDefinition, path)
        key = default.getRegistrationManager().setObject("", reg)
        self.reg = zapi.traverse(default.getRegistrationManager(), key)
        
    def tearDown(self):
        setup.placefulTearDown()

    def test_activated(self):
        self.reg.activated()
        service = zapi.getService(self.rootFolder, BrowserMenu)
        menu = service.getLocalMenu('add_content')
        self.assertEqual('TestDoc', menu['1'].title)
        self.assert_(self.reg.menuitem_id != None)
        self.assert_(self.reg.menu != None)
        self.assertEqual(menu, menu)

    def test_deactivated(self):
        self.test_activated()
        self.reg.deactivated()
        self.assertEqual(self.reg.menuitem_id, None)
        self.assertEqual(self.reg.menu, None)
        self.assertEqual(self.reg.getComponent().name,
                         '<component not activated>')


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
        unittest.makeSuite(ContentComponentInstanceTests),
        ))

if __name__ == '__main__':
    unittest.main()

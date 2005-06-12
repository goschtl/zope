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
"""Content Component Definition and Instance Tests

$Id$
"""
import unittest

from zope.component.exceptions import ComponentLookupError
from zope.interface import Interface, classImplements
from zope.schema import Int, TextLine, Text

from zope.app import zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.component.interfaces import ILocalUtility
from zope.app.container.interfaces import IAdding
from zope.app.schemacontent.content import \
     ContentComponentDefinition, ContentComponentDefinitionRegistration, \
     ContentComponentInstance
from zope.app.schemacontent.interfaces import IContentComponentDefinition
from zope.app.testing import setup, ztapi

class IDocument(Interface):
    id = Int(title=u"id", default=0)
    title = TextLine(title=u"title", default=u'Title goes here.')
    description = Text(title=u"desription")


class ContentComponentDefinitionRegistrationTests(unittest.TestCase):

    __name__ = __parent__ = None
    
    def setUp(self):
        setup.placefulSetUp()
        self.rootFolder = setup.buildSampleFolderTree()

        mgr = setup.createSiteManager(self.rootFolder)

        # Setup Definition
        classImplements(ContentComponentDefinition, ILocalUtility)
        classImplements(ContentComponentDefinition, IAttributeAnnotatable)
        default = zapi.traverse(mgr, 'default')
        default['TestDoc'] = ContentComponentDefinition()

        # Setup Definition Registration
        path = "%s/default/%s" % (zapi.getPath(mgr), 'TestDoc')
        reg = ContentComponentDefinitionRegistration(
            'TestDoc', IContentComponentDefinition, default['TestDoc'])
        key = default.registrationManager.addRegistration(reg)
        self.reg = zapi.traverse(default.registrationManager, key)
        
    def tearDown(self):
        setup.placefulTearDown()

    def test_activated(self):
        self.reg.activated()
        self.assertEqual(self.reg.component.name, 'TestDoc')

    def test_deactivated(self):
        self.test_activated()
        self.reg.deactivated()
        self.assertEqual(self.reg.component.name, None)


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
        self.assertEqual(doc.getSchema().__class__, IDocument.__class__)
        self.assertEqual(doc.getSchema().__dict__, IDocument.__dict__)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ContentComponentDefinitionRegistrationTests),
        unittest.makeSuite(ContentComponentInstanceTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

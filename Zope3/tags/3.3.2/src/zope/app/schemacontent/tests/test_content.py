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
from zope.testing import doctest
from zope.app.testing import placelesssetup

from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface, classImplements
from zope.schema import Int, TextLine, Text
from zope.annotation.interfaces import IAttributeAnnotatable

from zope.app import zapi
from zope.app.container.interfaces import IAdding
from zope.app.schemacontent.content import ContentComponentDefinition
from zope.app.schemacontent.content import ContentComponentInstance
from zope.app.schemacontent.content import registeredContentComponent
from zope.app.schemacontent.content import unregisteredContentComponent
from zope.app.schemacontent.interfaces import IContentComponentDefinition
from zope.app.testing import setup, ztapi

class IDocument(Interface):
    id = Int(title=u"id", default=0)
    title = TextLine(title=u"title", default=u'Title goes here.')
    description = Text(title=u"desription")

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

def test_subscribers():
    """
There seems to be a desire for ContentComponentDefinitions to know the
name they are registered under. The registeredContentComponent and
unregisteredContentComponent subscribers set or clear a definition's
name when the definition is registered or unregistered.

    >>> import zope.component.interfaces
    >>> class FauxRegistration:
    ...     name = u'bob'
    >>> definition = ContentComponentDefinition()
    >>> registeredContentComponent(
    ...     definition,
    ...     zope.component.interfaces.Registered(FauxRegistration)
    ...     )
    >>> definition.name
    u'bob'
    >>> unregisteredContentComponent(
    ...     definition,
    ...     zope.component.interfaces.Unregistered(FauxRegistration)
    ...     )
    >>> print definition.name
    None
    
"""

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ContentComponentInstanceTests),
        doctest.DocTestSuite(
            setUp=placelesssetup.setUp,
            tearDown=placelesssetup.tearDown,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

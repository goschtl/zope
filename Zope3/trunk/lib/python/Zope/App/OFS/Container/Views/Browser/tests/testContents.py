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

Revision information:
$Id: testContents.py,v 1.7 2002/11/18 23:52:59 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter

from Zope.App.OFS.Container.IZopeContainer import IZopeContainer
from Zope.App.OFS.Container.IContainer import IContainer
from Zope.App.OFS.Container.ZopeContainerAdapter import ZopeContainerAdapter

from Zope.Event.tests.PlacelessSetup import getEvents
from Zope.Event.IObjectEvent import IObjectRemovedEvent, IObjectModifiedEvent
from Interface import Interface
from Zope.Proxy.ProxyIntrospection import removeAllProxies


class BaseTestContentsBrowserView(PlacelessSetup):
    """Base class for testing browser contents.

    Subclasses need to define a method, '_TestView__newContext', that
    takes no arguments and that returns a new empty test view context.

    Subclasses need to define a method, '_TestView__newView', that
    takes a context object and that returns a new test view.
    """

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IContainer, IZopeContainer, ZopeContainerAdapter)    
        

    def testInfo(self):
        """ Do we get the correct information back from ContainerContents? """
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container.setObject( 'subcontainer', subcontainer )
        document = Document()
        container.setObject( 'document', document )

        fc = self._TestView__newView( container )
        info_list = fc.listContentInfo()

        self.assertEquals( len( info_list ), 2 )

        ids = map( lambda x: x['id'], info_list )
        self.assert_( 'subcontainer' in ids )

        objects = map( lambda x: x['object'], info_list )
        self.assert_( subcontainer in objects )

        urls = map( lambda x: x['url'], info_list )
        self.assert_( 'subcontainer' in urls )

        self.failIf( filter( None, map( lambda x: x['icon'], info_list ) ) )

    def testInfoWDublinCore(self):
        container = self._TestView__newContext()
        document = Document()
        container.setObject( 'document', document )

        from datetime import datetime
        from Zope.App.DublinCore.IZopeDublinCore import IZopeDublinCore

        class FauxDCAdapter:
            __implements__ = IZopeDublinCore
            
            def __init__(self, context):
                pass
            title = 'faux title'
            created = datetime(2001, 1, 1, 1, 1, 1)
            modified = datetime(2002, 2, 2, 2, 2, 2)

        from Zope.ComponentArchitecture.GlobalAdapterService \
             import provideAdapter
        provideAdapter(IDocument, IZopeDublinCore, FauxDCAdapter)
        
        fc = self._TestView__newView( container )
        info = fc.listContentInfo()[0]

        self.assertEqual(info['id'], 'document')
        self.assertEqual(info['url'], 'document')
        self.assertEqual(info['object'], document)
        self.assertEqual(info['title'], 'faux title')
        self.assertEqual(info['created'], FauxDCAdapter.created)
        self.assertEqual(info['modified'], FauxDCAdapter.modified)

    def testRemove( self ):
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container.setObject('subcontainer', subcontainer)
        document = Document()
        container.setObject('document', document)
        document2 = Document()
        container.setObject('document2', document2)

        fc = self._TestView__newView( container )

        self.failIf(getEvents(IObjectModifiedEvent))
        self.failIf(getEvents(IObjectRemovedEvent))

        fc.removeObjects(['document2'])

        self.failUnless(
            getEvents(IObjectRemovedEvent,
                      filter =
                      lambda event:
                      removeAllProxies(event.object) == document2)
            )
        self.failUnless(
            getEvents(IObjectModifiedEvent,
                      filter =
                      lambda event:
                      removeAllProxies(event.object) == container)
            )
        
        info_list = fc.listContentInfo()

        self.assertEquals( len( info_list ), 2 )

        ids = map( lambda x: x['id'], info_list )
        self.assert_( 'subcontainer' in ids )

        objects = map( lambda x: x['object'], info_list )
        self.assert_( subcontainer in objects )

        urls = map( lambda x: x['url'], info_list )
        self.assert_( 'subcontainer' in urls )


class IDocument(Interface):
    pass

class Document:
    __implements__ = IDocument


class Test(BaseTestContentsBrowserView, TestCase):

    def _TestView__newContext(self):
        from Zope.App.OFS.Container.SampleContainer import SampleContainer
        return SampleContainer()

    def _TestView__newView(self, container):
        from Zope.App.OFS.Container.Views.Browser.Contents import Contents
        from Zope.Publisher.Browser.BrowserRequest import TestRequest
        return Contents(container, TestRequest())

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')

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
$Id: testContents.py,v 1.5 2002/07/17 16:54:17 jeremy Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter

from Zope.I18n.IUserPreferredCharsets import IUserPreferredCharsets

from Zope.Publisher.HTTP.HTTPRequest import IHTTPRequest
from Zope.Publisher.HTTP.HTTPCharsets import HTTPCharsets


class BaseTestContentsBrowserView(PlacelessSetup):
    """Base class for testing browser contents.

    Subclasses need to define a method, '_TestView__newContext', that
    takes no arguments and that returns a new empty test view context.

    Subclasses need to define a method, '_TestView__newView', that
    takes a context object and that returns a new test view.
    """

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)
        

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

        titles = map( lambda x: x['title'], info_list )
        self.assert_( 'subcontainer' in titles )

        urls = map( lambda x: x['url'], info_list )
        self.assert_( 'subcontainer' in urls )

        self.failIf( filter( None, map( lambda x: x['icon'], info_list ) ) )

    def testRemove( self ):
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container.setObject( 'subcontainer', subcontainer )
        document = Document()
        container.setObject( 'document', document )
        container.setObject( 'document2', Document() )

        fc = self._TestView__newView( container )
        fc.remove( name='document2' )
        info_list = fc.listContentInfo()

        self.assertEquals( len( info_list ), 2 )

        ids = map( lambda x: x['id'], info_list )
        self.assert_( 'subcontainer' in ids )

        objects = map( lambda x: x['object'], info_list )
        self.assert_( subcontainer in objects )

        titles = map( lambda x: x['title'], info_list )
        self.assert_( 'subcontainer' in titles )

        urls = map( lambda x: x['url'], info_list )
        self.assert_( 'subcontainer' in urls )

        self.assertRaises( KeyError, fc.remove, 'document3' )

        fc.remove( 'document3', 1 )


class Document:
    pass


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

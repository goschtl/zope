##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
""" Unit tests for CMFCore.TextFilters. """

import unittest

SAMPLE_TEXT = """Sample text"""

class TextInfoTests( unittest.TestCase ):

    def _testInitialValues( self, info, text=SAMPLE_TEXT, **kwargs ):

        self.assertEqual( info.getText(), text )
        self.assertEqual( info(), text )
        self.assertEqual( len( info.keys() ), len( kwargs ) )
        for k,v in kwargs.items():
            self.assertEqual( info.get( k ), v )

    def testInterface( self ):

        from Products.CMFCore.interfaces.portal_textmanager import TextInfo
        from Products.CMFCore.TextFilters import TextInfoImpl

        self.failUnless( TextInfo.isImplementedByInstancesOf( TextInfoImpl ) )


    def testInitFromString( self ):

        from Products.CMFCore.TextFilters import _makeTextInfo

        info = _makeTextInfo( SAMPLE_TEXT )
        self._testInitialValues( info )

    def testInitFromDict( self ):

        from Products.CMFCore.TextFilters import _makeTextInfo

        info = _makeTextInfo( { 'text' : SAMPLE_TEXT } )
        self._testInitialValues( info )

        info = _makeTextInfo( { 'text' : SAMPLE_TEXT
                             , 'foo'  : 'bar'
                             } )
        self._testInitialValues( info, foo='bar' )

    def testInitFromInfo( self ):

        from Products.CMFCore.TextFilters import _makeTextInfo

        source = _makeTextInfo( SAMPLE_TEXT )
        info = _makeTextInfo( source )
        self._testInitialValues( info )
        info[ 'foo' ] = 'bar'
        info2 = _makeTextInfo( info )
        self._testInitialValues( info, foo='bar' )

class PassthroughFilterTests( unittest.TestCase ):

    def testInterface( self ):

        from Products.CMFCore.interfaces.portal_textmanager import TextFilter
        from Products.CMFCore.TextFilters import PassthroughFilter

        self.failUnless(
                TextFilter.isImplementedByInstancesOf( PassthroughFilter ) )

    def testSimple( self ):

        from Products.CMFCore.TextFilters import PassthroughFilter
        pt = PassthroughFilter()

        ti = pt()
        self.failIf( ti() )

        ti = pt( '' )
        self.assertEqual( ti(), '' )

        ti = pt( SAMPLE_TEXT )
        self.assertEqual( ti(), SAMPLE_TEXT )

        ti = pt( ti )
        self.assertEqual( ti(), SAMPLE_TEXT )

HTML_TEMPLATE = '''\
<html><head>
 <title>%(title)s</title>
</head>
<body>%(body)s</body>
</html>
'''

HTML_TEMPLATE_WITH_METADATA = '''\
<html><head>
 <title>%(title)s</title>
 <meta name="description" content="%(description)s" />
 <meta name="keywords" content="%(keywords)s" />
</head>
<body>%(body)s</body>
</html>
'''

class HTMLDecapitatorTests( unittest.TestCase ):

    def testInterface( self ):

        from Products.CMFCore.interfaces.portal_textmanager import TextFilter
        from Products.CMFCore.TextFilters import HTMLDecapitator

        self.failUnless(
                TextFilter.isImplementedByInstancesOf( HTMLDecapitator ) )

    def testChopSimple( self ):

        from Products.CMFCore.TextFilters import HTMLDecapitator
        chopper = HTMLDecapitator()

        HTML = HTML_TEMPLATE % { 'title' : 'Sample title'
                               , 'body' : SAMPLE_TEXT
                               }
        
        ti = chopper.filterText( HTML )

        self.assertEqual( ti(), SAMPLE_TEXT )
        self.failUnless( ti[ 'metadata' ] )
        self.assertEqual( ti[ 'metadata' ][ 'Title' ], 'Sample title' )

    def testChopWithMeta( self ):

        from Products.CMFCore.TextFilters import HTMLDecapitator
        chopper = HTMLDecapitator()

        HTML = (
            HTML_TEMPLATE_WITH_METADATA % { 'title' : 'Sample title'
                                          , 'body' : SAMPLE_TEXT
                                          , 'description' : 'Sample description'
                                          , 'keywords' : 'sample, test'
                                          } )
        
        ti = chopper.filterText( HTML )

        self.assertEqual( ti(), SAMPLE_TEXT )
        md = ti[ 'metadata' ]
        self.assertEqual( md.get( 'Title', None ), 'Sample title' )
        self.assertEqual( md.get(  'Description', None ), 'Sample description' )

        subject = md.get( 'Subject', () )
        self.assertEqual( len( subject ), 2 )
        self.failUnless( 'sample' in subject )
        self.failUnless( 'test'   in subject )


STX_TEMPLATE = """\
Title: %(title)s
Description: %(description)s

%(body)s"""

class STXDecapitatorTests( unittest.TestCase ):

    def testInterface( self ):

        from Products.CMFCore.interfaces.portal_textmanager import TextFilter
        from Products.CMFCore.TextFilters import STXDecapitator

        self.failUnless(
                TextFilter.isImplementedByInstancesOf( STXDecapitator ) )

    def testChopNoHeaders( self ):

        from Products.CMFCore.TextFilters import STXDecapitator
        chopper = STXDecapitator()

        ti = chopper.filterText( SAMPLE_TEXT )
        self.assertEqual( ti(), SAMPLE_TEXT )
        self.failIf( ti[ 'metadata' ] )

    def testChopWithHeaders( self ):

        from Products.CMFCore.TextFilters import STXDecapitator
        chopper = STXDecapitator()

        STX = STX_TEMPLATE % { 'title' : 'Sample Title'
                             , 'description' : 'Sample description'
                             , 'body' : SAMPLE_TEXT
                             }

        ti = chopper.filterText( STX )
        self.assertEqual( ti(), SAMPLE_TEXT )
        md = ti[ 'metadata' ]

        self.assertEqual( md[ 'Title' ], 'Sample Title' )
        self.assertEqual( md[ 'Description' ], 'Sample description' )


PLAIN_TEXT_WITH_PARAGRAPHS = """\
This is the first paragraph.  It contains just enough text that we have to
wrap it.

This is the second paragraph.
"""

class ParagraphInserterTests( unittest.TestCase ):

    def testInterface( self ):

        from Products.CMFCore.interfaces.portal_textmanager import TextFilter
        from Products.CMFCore.TextFilters import ParagraphInserter

        self.failUnless(
                TextFilter.isImplementedByInstancesOf( ParagraphInserter ) )

    def _makePattern( self ):
        import re
        return re.compile( r'<p>(.*?)</p>', re.MULTILINE | re.DOTALL )

    def testInsertEmpty( self ):

        from Products.CMFCore.TextFilters import ParagraphInserter

        inserter = ParagraphInserter()

        ti = inserter.filterText( '' )
        text = ti()

        graphs = self._makePattern().findall( text )
        self.assertEqual( len( graphs ), 0 )

    def testInsertOneGraph( self ):

        from Products.CMFCore.TextFilters import ParagraphInserter

        inserter = ParagraphInserter()

        ti = inserter.filterText( SAMPLE_TEXT )
        text = ti()

        graphs = self._makePattern().findall( text )
        self.assertEqual( len( graphs ), 1 )

    def testInsertTwoGraphs( self ):

        from Products.CMFCore.TextFilters import ParagraphInserter

        inserter = ParagraphInserter()

        ti = inserter.filterText( PLAIN_TEXT_WITH_PARAGRAPHS )
        text = ti()

        graphs = self._makePattern().findall( text )
        self.assertEqual( len( graphs ), 2 )

    def testInsertManyGraphs( self ):

        from Products.CMFCore.TextFilters import ParagraphInserter
        import string

        inserter = ParagraphInserter()

        graphs = [PLAIN_TEXT_WITH_PARAGRAPHS] * 12
        text = string.join( graphs, '\n\n' )

        ti = inserter.filterText( text )
        text = ti()

        graphs = self._makePattern().findall( text )
        self.assertEqual( len( graphs ), 24 )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( TextInfoTests ) )
    suite.addTest( unittest.makeSuite( PassthroughFilterTests ) )
    suite.addTest( unittest.makeSuite( HTMLDecapitatorTests ) )
    suite.addTest( unittest.makeSuite( STXDecapitatorTests ) )
    suite.addTest( unittest.makeSuite( ParagraphInserterTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()

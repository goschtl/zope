from unittest import TestSuite, makeSuite, main
from StringIO import StringIO
from re import compile

from Products.CMFCore.tests.base.testcase import \
     RequestTest

from Products.CMFDefault.Document import Document

DOCTYPE = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'''

HTML_TEMPLATE = '''\
<html><head>
 <title>%(title)s</title>
</head>
<body bgcolor="#efe843">%(body)s</body>
</html>
'''

BASIC_HTML = '''\
<html>
 <head>
  <title>Title in tag</title>
  <meta name="description" content="Describe me">
  <meta name="contributors" content="foo@bar.com; baz@bam.net;
    Benotz, Larry J (larry@benotz.stuff)">
  <meta name="title" content="Title in meta">
  <meta name="subject" content="content management">
  <meta name="keywords" content="unit tests, framework; ,zope ">
 </head>
 <body bgcolor="#ffffff">
  <h1>Not a lot here</h1>
 </body>
</html>
'''

SIMPLE_HTML = '''\
<html>
 <head>
  <title>Title in tag</title>
  <meta name="description" content="Describe me">
  <meta name="contributors" content="foo@bar.com; baz@bam.net;
    Benotz, Larry J (larry@benotz.stuff)">
  <meta name="title" content="Title in meta">
  <meta name="subject" content="content management">
 </head>
 <body bgcolor="#ffffff">
  <h1>Not a lot here</h1>
 </body>
</html>
'''

ENTITY_IN_TITLE = '''\
<html>
 <head>
  <title>&Auuml;rger</title>
 </head>
 <bOdY>
  <h2>Not a lot here either</h2>
 </bodY>
</html>
'''

BASIC_STRUCTUREDTEXT = '''\
Title: My Document
Description: A document by me
Contributors: foo@bar.com; baz@bam.net; no@yes.maybe
Subject: content management, zope
Keywords: unit tests; , framework

This is the header

  Body body body body body
  body body body.

   o A list item
   
   o And another thing...
'''

SIMPLE_STRUCTUREDTEXT = '''\
Title: My Document
Description: A document by me
Contributors: foo@bar.com; baz@bam.net; no@yes.maybe
Subject: content management, zope

This is the header

  Body body body body body
  body body body.

   o A list item
   
   o And another thing...
'''

STX_WITH_HTML = """\
Sometimes people do interesting things

  Sometimes people do interesting things like have examples
  of HTML inside their structured text document.  We should
  be detecting that this is indeed a structured text document
  and **NOT** an HTML document::

    <html>
    <head><title>Hello World</title></head>
    <body><p>Hello world, I am Bruce.</p></body>
    </html>

  All in favor say pi!
"""

STX_NO_HEADERS = """\
Title Phrase

    This is a "plain" STX file, with no headers.  Saving with
    it shouldn't overwrite any metadata.
"""

STX_NO_HEADERS_BUT_COLON = """\
Plain STX:  No magic!

    This is a "plain" STX file, with no headers.  Saving with
    it shouldn't overwrite any metadata.
"""

class DocumentTests(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        self.d = Document('foo')

    def test_Empty(self):
        d = Document('foo', text_format='structured-text')
        self.assertEqual( d.title, '' )
        self.assertEqual( d.description, '' )
        self.assertEqual( d.text, '' )
        self.assertEqual( d.text_format, 'structured-text' )
        self.assertEqual( d._stx_level, 1 )

    def test_BasicHtmlPUT(self):
        self.REQUEST['BODY'] = BASIC_HTML
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.title, 'Title in tag' )
        self.assertEqual( d.text.find('</body>'), -1 )
        self.assertEqual( d.Description(), 'Describe me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.assertEqual( d.Contributors()[-1], 'Benotz, Larry J (larry@benotz.stuff)' )

        # Since the format is html, the STX level operands should
        # have no effect.
        ct = d.CookedBody(stx_level=3, setlevel=1)
        self.assertEqual( d._stx_level, 1 )

        subj = list(d.Subject())
        self.assertEqual( len(subj), 4 )
        subj.sort()
        self.assertEqual( subj, [ 'content management'
                                , 'framework'
                                , 'unit tests'
                                , 'zope'
                                ] )

    def test_UpperedHtml(self):
        self.REQUEST['BODY'] = BASIC_HTML.upper()
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.title, 'TITLE IN TAG' )
        self.assertEqual( d.text.find('</BODY'), -1 )
        self.assertEqual( d.Description(), 'DESCRIBE ME' )
        self.assertEqual( len(d.Contributors()), 3 )

    def test_EntityInTitle(self):
        self.REQUEST['BODY'] = ENTITY_IN_TITLE 
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.title, '&Auuml;rger' )

    def test_HtmlWithDoctype(self):
        d = self.d
        self.REQUEST['BODY'] = '%s\n%s' % (DOCTYPE, BASIC_HTML)
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Description(), 'Describe me' )

    def test_HtmlWithoutNewlines(self):
        d = self.d
        self.REQUEST['BODY'] = ''.join((BASIC_HTML.split('\n')))
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Description(), 'Describe me' )

    def test_BigHtml(self):
        d = self.d
        s = []
        looper = '<li> number %s</li>'
        for i in range(12000): s.append(looper % i)
        body = '<ul>\n%s\n</ul>' % '\n'.join(s)
        self.REQUEST['BODY'] = HTML_TEMPLATE % {'title': 'big document',
                                'body': body}
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.CookedBody(), body )

    def test_BigHtml_via_upload(self):
        d = self.d
        s = []
        looper = '<li> number %s</li>'
        for i in range(12000): s.append(looper % i)
        body = '<ul>\n%s\n</ul>' % '\n'.join(s)
        html = HTML_TEMPLATE % {'title': 'big document',
                                'body': body}
        file = StringIO( html )
        d.edit(text_format='html', text='', file=file)
        self.assertEqual( d.CookedBody(), body )
        

    def test_EditStructuredTextWithHTML(self):
        d = self.d
        d.edit(text_format='structured-text', text=STX_WITH_HTML)
        
        self.assertEqual( d.Format(), 'text/plain' )

    def test_StructuredText(self):
        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.failUnless( hasattr(d, 'cooked_text') )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'My Document' )
        self.assertEqual( d.Description(), 'A document by me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( d.cooked_text.find('<p>') >= 0 )
        self.failUnless( d.CookedBody().find('<h1') >= 0 )

        # Make sure extra HTML is NOT found
        self.failUnless( d.cooked_text.find('<title>') < 0 )
        self.failUnless( d.cooked_text.find('<body>') < 0 )

        # test subject/keyword headers
        subj = list(d.Subject())
        self.assertEqual( len(subj), 4 )
        subj.sort()
        self.assertEqual( subj, [ 'content management'
                                , 'framework'
                                , 'unit tests'
                                , 'zope'
                                ] )

    def test_STX_Levels(self):
        d = self.d
        d.edit(text_format='structured-text', text=BASIC_STRUCTUREDTEXT)
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody()
        self.failUnless( d.CookedBody().find('<h1') >= 0 )
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody(stx_level=2)
        self.failIf( ct.find('<h1') >= 0 )
        self.failUnless( ct.find('<h2') >= 0 )
        self.assertEqual( d._stx_level, 1 )

        ct = d.CookedBody(stx_level=2, setlevel=1)
        self.failIf( ct.find('<h1') >= 0 )
        self.failUnless( ct.find('<h2') >= 0 )
        self.assertEqual( d._stx_level, 2 )

        ct = d.CookedBody()
        self.assertEqual( d._stx_level, 2 )
        self.failIf( d.CookedBody().find('<h1') >= 0 )
        self.failUnless( d.CookedBody().find('<h2') >= 0 )

    def test_Init(self):
        self.REQUEST['BODY']=BASIC_STRUCTUREDTEXT
        d = self.d
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'My Document' )
        self.assertEqual( d.Description(), 'A document by me' )
        self.assertEqual( len(d.Contributors()), 3 )
        self.failUnless( d.cooked_text.find('<p>') >= 0 )

        d = Document('foo', text='')
        self.REQUEST['BODY']=BASIC_HTML
        d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Title(), 'Title in tag' )
        self.assertEqual( len(d.Contributors()), 3 )

        d = Document('foo', text_format='structured-text', title='Foodoc')
        self.assertEqual( d.text, '' )
        self.failIf( d.CookedBody() )
        self.assertEqual( d.title, 'Foodoc' )
        self.assertEqual( d.Format(), 'text/plain' )

        # Tracker issue 435:  initial text is not cooked.
        d = Document('foo', text_format='structured-text', text=STX_NO_HEADERS)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS )
        self.failUnless( d.CookedBody() )
        self.assertEqual( d.Format(), 'text/plain' )
    
    def test_STX_NoHeaders( self ):
        self.REQUEST['BODY']=STX_NO_HEADERS
        d = self.d
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )
        self.assertEqual( d.Format(), 'text/html' )
        self.assertEqual( d.Title(), 'Plain STX' )
        self.assertEqual( d.Description(), 'Look, Ma, no headers!' )
        self.assertEqual( len( d.Subject() ), 2 )
        self.failUnless( 'plain' in d.Subject() )
        self.failUnless( 'STX' in d.Subject() )

        d.PUT(self.REQUEST, self.RESPONSE)
        
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Title(), 'Plain STX' )
        self.assertEqual( d.Description(), 'Look, Ma, no headers!' )
        self.assertEqual( len( d.Subject() ), 2 )
        self.failUnless( 'plain' in d.Subject() )
        self.failUnless( 'STX' in d.Subject() )
    
    def test_STX_NoHeaders_but_colon( self ):
        d = self.d
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )

        d.edit(text_format='structured-text', text=STX_NO_HEADERS_BUT_COLON)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS_BUT_COLON )
    
    def test_ZMI_edit( self ):
        d = self.d
        d.editMetadata( title="Plain STX"
                       , description="Look, Ma, no headers!"
                       , subject=( "plain", "STX" )
                       )

        d.manage_editDocument( text_format='structured-text'
                             , text=STX_NO_HEADERS_BUT_COLON)
        self.assertEqual( d.EditableBody(), STX_NO_HEADERS_BUT_COLON )


class TestFTPGet( RequestTest ):

    def testHTML( self ):
        self.REQUEST['BODY']=SIMPLE_HTML
        d = Document( 'foo' )
        d.PUT(self.REQUEST, self.RESPONSE)

        rnlinesplit = compile( r'\r?\n?' )
        simple_lines = rnlinesplit.split( SIMPLE_HTML )
        get_lines = rnlinesplit.split( d.manage_FTPget() )

        # strip off headers
        meta_pattern = compile( r'meta name="([a-z]*)" '
                                 + r'content="([a-z]*)"'
                                 )
        title_pattern = compile( r'<title>(.*)</title>' )
        simple_headers = []
        while simple_lines and simple_lines[0] != '<BODY>':
            header = simple_lines[0].strip().lower() 
            match = meta_pattern.search( header )
            if match:
                simple_headers.append( match.groups() )
            else:
                match = title_pattern.search( header )
                if match:
                    simple_headers.append( ( 'title', match.group(1) ) )
            simple_lines = simple_lines[1:]

        get_headers = []
        while get_lines and get_lines[0] != '<BODY>':
            header = get_lines[0].strip().lower()
            match = meta_pattern.search( header )
            if match:
                get_headers.append( match.groups() )
            else:
                match = title_pattern.search( header )
                if match:
                    get_headers.append( ( 'title', match.group(1) ) )
            get_lines = get_lines[1:]

        self.assertEqual( get_lines, simple_lines )

        self.failUnless( get_headers )
        self.failUnless( simple_headers )
        self.failUnless( len( get_headers ) >= len( simple_headers ) )

        for header in simple_headers:
            self.failUnless( header in get_headers )

    def testSTX( self ):
        self.REQUEST['BODY']=SIMPLE_STRUCTUREDTEXT
        d = Document( 'foo' )
        d.PUT(self.REQUEST, self.RESPONSE)

        rnlinesplit = compile( r'\r?\n?' )

        get_text = d.manage_FTPget()
        simple_lines = rnlinesplit.split( SIMPLE_STRUCTUREDTEXT )
        get_lines = rnlinesplit.split( get_text )

        # strip off headers
        simple_headers = []
        while simple_lines and simple_lines[0]:
            simple_headers.append( simple_lines[0] )
            simple_lines = simple_lines[1:]

        get_headers = []
        while get_lines and get_lines[0]:
            get_headers.append( get_lines[0] )
            get_lines = get_lines[1:]

        self.assertEqual( get_lines, simple_lines )

        for header in simple_headers:
            self.failUnless( header in get_headers )

class TestDocumentPUT(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        self.d = Document('foo')

    def test_PutStructuredTextWithHTML(self):
            
        self.REQUEST['BODY'] = STX_WITH_HTML

        r = self.d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( self.d.Format(), 'text/plain' )
        self.assertEqual( r.status, 204 )

    def test_PutStructuredText(self):

        self.REQUEST['BODY'] = BASIC_STRUCTUREDTEXT

        r = self.d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( self.d.Format(), 'text/plain' )
        self.assertEqual( r.status, 204 )

    def test_PutHtmlWithDoctype(self):
        
        html = '%s\n\n  \n   %s' % (DOCTYPE, BASIC_HTML)
        self.REQUEST['BODY'] = html
        
        r = self.d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( self.d.Format(), 'text/html' )
        self.assertEqual( self.d.Description(), 'Describe me' )
        self.assertEqual( r.status, 204 )

    def test_PutHtml(self):
        
        self.REQUEST['BODY'] = BASIC_HTML
        r = self.d.PUT(self.REQUEST, self.RESPONSE)
        self.assertEqual( self.d.Format(), 'text/html' )
        self.assertEqual( self.d.Description(), 'Describe me' )
        self.assertEqual( r.status, 204 )


def test_suite():
    return TestSuite((
        makeSuite(DocumentTests),
        makeSuite(TestFTPGet),
        makeSuite(TestDocumentPUT),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')


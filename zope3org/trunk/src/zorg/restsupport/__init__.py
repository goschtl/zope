##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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

import sgmllib

from cStringIO import StringIO
from zope.app.renderer.rest import ReStructuredTextSourceFactory
from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer
from zope.app.renderer.rest import ZopeTranslator

from docutils.parsers.rst.directives import misc
del misc.raw
del misc.include;

from zorg.restsupport.html2rest import Html2ReStructuredTextParser


def rest2html(rest) :
    """ Converts rest to html.
    
    >>> rest = '''======
    ... Header
    ... ======
    ... 
    ... Test
    ... '''
    >>> print rest2html(rest)
    <h1 class="title">Header</h1>
    <p>Test</p>
    <BLANKLINE>

    """
   
    if not isinstance(rest, unicode) :
        rest = unicode(rest, encoding='utf-8', errors='replace')
    main = ReStructuredTextSourceFactory(rest)
    renderer = ReStructuredTextToHTMLRenderer(main, None)
    return renderer.render()
                

def html2rest(html, fragment=False, catch_errors=True) :
    """ Converts html to rest. 
    
    >>> html = '<html><body><h1>Header</h1><p>Test</p></body></html>'
    >>> print html2rest(html)
    ======
    Header
    ======
    <BLANKLINE>
    Test
    <BLANKLINE>

    If an error occurs the input HTML is returned
    unmodified with an error prefix :
    
    >>> html = '<h1>Header</h1><p>Test</p>'
    >>> print html2rest(html)
    Sorry, cannot convert to ReST:
    <h1>Header</h1><p>Test</p>
    
    >>> print html2rest(html, fragment=True)
    ======
    Header
    ======
    <BLANKLINE>
    Test
    <BLANKLINE>
    
    """
        
    if fragment and not '<html>' in html.lower() :
        if html :
            html = "<html><body>%s</body></html>" % html
        else :
            return ""
        
    if catch_errors :
        try :
            parser = Html2ReStructuredTextParser()
            parser.feed(html)
            while parser.current:
                parser.pop_para()
            lines = parser.para.get_content(parser.page_width)
            if lines :
                return "\n".join(lines)
            else :
                return "Sorry, cannot convert to ReST:\n" + html
        except :
            return "Sorry, cannot convert to ReST:\n" + html
    else :
        parser = Html2ReStructuredTextParser()
        parser.feed(html)
        while parser.current:
            parser.pop_para()
        lines = parser.para.get_content(parser.page_width)
        if not lines :
            raise RuntimeError, "cannot convert fragments"
        return "\n".join(lines)



def guess_html(text) :
    """
    Tries to guess wether a text is html. Extracts the tags
    and returns true if the text contains tags.
    
    Modified from 
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/303227
    
    >>> guess_html("paragraph")
    False
    
    >>> guess_html("<p>paragraph</p>")
    True
    
    """
    
    class Cleaner(sgmllib.SGMLParser):
    
      entitydefs={"nbsp": " "}
    
      def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = []
        
      def do_p(self, *junk):
        self.result.append('\n')
        
      def do_br(self, *junk):
        self.result.append('\n')
        
      def handle_data(self, data):
        self.result.append(data)
        
      def cleaned_text(self):
        return ''.join(self.result)

    def stripHTML(text):
      c=Cleaner()
      try:
        c.feed(text)
      except sgmllib.SGMLParseError:
        return text
      else:
        t=c.cleaned_text()
        return t
        
    lt=len(text)
    if lt==0:
        return False
    textWithoutTags=stripHTML(text)
    tagsChars=lt-len(textWithoutTags)
    return tagsChars > 0
    
def text2html(text) :
    """ Converts rest to html if necessary. 
    
    >>> print text2html('<p>A paragraph</p>')
    <p>A paragraph</p>
    
    >>> print text2html("A paragraph")
    <p>A paragraph</p>
    <BLANKLINE>
    
    """
    if guess_html(text) :
        return text
    return rest2html(text)
    
    
def text2rest(text) :
    """ Converts html to rest if necessary. 
    
    >>> print text2rest('<p>A paragraph</p>')
    A paragraph
    <BLANKLINE>
    
    """
    if guess_html(text) :
        return html2rest(text, fragment=True)
    return text
    
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
import unittest, doctest

from cStringIO import StringIO
from zope.app.renderer.rest import ReStructuredTextSourceFactory
from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer
from zope.app.renderer.rest import ZopeTranslator


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
   
    main = ReStructuredTextSourceFactory(rest)
    renderer = ReStructuredTextToHTMLRenderer(main, None)
    return renderer.render()
                
              
def html2rest(html) :
    """ Converts html to rest. 
    
    >>> html = '<html><body><h1>Header</h1><p>Test</p></body></html>'
    >>> print html2rest(html)
    ======
    Header
    ======
    <BLANKLINE>
    Test
    <BLANKLINE>

    Fragments can not be processed :
    
    >>> html = '<h1>Header</h1><p>Test</p>'
    >>> print html2rest(html)
    <BLANKLINE>

    """
    
    parser = Html2ReStructuredTextParser()
    parser.feed(html)
    while parser.current:
        parser.pop_para()
    lines = parser.para.get_content(parser.page_width)
    return "\n".join(lines)    
 
 
def test_suite():
    
    return unittest.TestSuite((
        doctest.DocTestSuite(),))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


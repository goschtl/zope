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
"""
    Common text filters.
"""

from Products.CMFCore.interfaces.portal_textmanager import TextFilter, TextInfo
from UserDict import UserDict
import re

class TextInfoImpl( UserDict ):
    """
        Hold on to a chunk of text, plus additional data about the
        text, as munged by one or more TextFilter implementations.
    """
    __implements__ = TextInfo

    _text = ''

    def getText( self ):
        return self._text

    def setText( self, text ):
        self._text = text

    __call__ = getText


class PassthroughFilter:
    """
        No-op filter;  just makes sure that next-in-line gets a true
        TextInfo.
    """
    __implements__ = TextFilter

    def filterText( self, text_info='' ):

        return _ensureTextInfo( text_info )

    __call__ = filterText


class HTMLDecapitator:
    """
        Strip everything outside of <body> from an HTML document;
        stash data from <head> contents in extra data.
    """
    __implements__ = TextFilter

    def _processMetadata( self  
                        , parser
                        , splitter=re.compile( r'[, ]+' )
                        ):
        """
            Post-process metadata extracted from <meta> tags to match
            DublinCore.
        """
        result = {}

        result[ 'Title' ] = parser.title or ''

        for k, v in parser.metatags.items():

            if k == 'Keywords':
                k = 'Subject'

            if k in ( 'Subject', 'Contributors' ):
                v = splitter.split( v )
        
            result[ k ] = v

        return result

    def filterText( self, text_info='' ):

        text_info = _ensureTextInfo( text_info )
        result = _makeTextInfo( text_info )

        text = text_info()
        result.setText( _bodyfinder( text ) )

        parser = _SimpleHTMLParser()
        parser.feed( text )
        result[ 'metadata' ] = self._processMetadata( parser )

        return result

    __call__ = filterText


class STXDecapitator:
    """
        Strip leading RFC822-style metadata headers from a StructuredText
        document;  stash metadata in extra data.
    """
    __implements__ = TextFilter

    def filterText( self, text_info='' ):

        text_info = _ensureTextInfo( text_info )
        result = _makeTextInfo( text_info )

        text = text_info()

        headers, body = _parseSTXHeadersBody( text )
        result.setText( body )

        result[ 'metadata' ] = headers

        return result

    __call__ = filterText


class ParagraphInserter:
    """
        Convert "plain" text to paragraph-separated HTML.
    """
    __implements__ = TextFilter

    def filterText( self
                  , text_info=''
                  , DOUBLE_NEWLINE=re.compile( r'\n\n' )
                  ):
        text_info = _ensureTextInfo( text_info )
        result = _makeTextInfo( text_info )

        graphs = []
        for graph in DOUBLE_NEWLINE.split( text_info() ):

            while graph and graph[-1] == '\n':
                graph = graph[ :-1 ]

            if not graph:
                continue

            graph = '<p>%s</p>' % graph
            graphs.append( graph )

        result.setText( join( graphs, '\n' ) )

        return result

    __call__ = filterText


class Pipeline:
    """
        Composite filter, chaining a list of filters together.
    """
    __implements__ = TextFilter

    _filters = ()

    def filterText( self, text_info='' ):

        next = _ensureTextInfo( text_info )

        for filter in self._filters:
            next = filter.filterText( next )

        return next

    __call__ = filterText

    def addFilter( self, filter ):
        """
            Append 'filter' to the end of our chain;  'filter' must
            implement TextFilter.
        """
        if not TextFilter.isImplementedBy( filter ):
            raise ValueError, 'Not a filter.'

        self._filters = self._filters + ( filter, )


#
#   Helper functions & classes
#
from sgmllib import SGMLParser
from string import join, capitalize   # XXX: WAAAA!  2.3 compatibility


def _makeTextInfo( text_or_info ):
    """
        Create and return a TextInfoImpl instance using 'text_or_info'.
    """
    result = TextInfoImpl()

    if TextInfo.isImplementedBy( text_or_info ):
        result.update( text_or_info )
        result.setText( text_or_info() )

    elif type( text_or_info ) in ( type( '' ), type( u'' ) ):
        result.setText( text_or_info )

    elif type( text_or_info ) is type( {} ):
        for k,v in filter( lambda x: x[0] != 'text', text_or_info.items() ):
            result[ k ] = v
        result.setText( text_or_info.get( 'text', '' ) )

    return result


def _ensureTextInfo( text_or_info ):
    """
        Guarantee that 'text_or_info' is a TextInfo (force it by creating
        a new instance, if necessary).
    """
    if TextInfo.isImplementedBy( text_or_info ):
        return text_or_info

    return _makeTextInfo( text_or_info )


class _SimpleHTMLParser(SGMLParser):
    """
        Parse off header tags from an HTML document, collecting the
        data from the tags into attributes.

        TODO:  Capture <style>, <script>?  (Why, for content?)
    """

    def __init__(self, verbose=0):
        SGMLParser.__init__(self, verbose)
        self.savedata = None
        self.title = ''
        self.metatags = {}
        self.links = []

    def handle_data(self, data):
        if self.savedata is not None:
            self.savedata = self.savedata + data

    def handle_charref(self, ref):
        self.handle_data("&#%s;" % ref)

    def handle_entityref(self, ref):
        self.handle_data("&%s;" % ref)

    def save_bgn(self):
        self.savedata = ''

    def save_end(self):
        data = self.savedata
        self.savedata = None
        return data

    def start_title(self, attrs):
        self.save_bgn()

    def end_title(self):
        self.title = self.save_end()

    def do_meta(self, attrs):
        name = ''
        content = ''
        for attrname, value in attrs:
            value = value.strip()
            if attrname == "name": name = capitalize( value )
            if attrname == "content": content = value
        if name:
            self.metatags[name] = content

    def do_link( self, attrs ):
        link_data = {}
        for k,v in attrs:
            link_data[ k ] = v
        self.links.append( link_data )
    
    def unknown_startag(self, tag, attrs):
        self.setliteral()

    def unknown_endtag(self, tag):
        self.setliteral()
    

def _bodyfinder( text
               , BODYSTART = re.compile(r'<body.*?>', re.DOTALL|re.I)
               , BODYEND = re.compile(r'</body', re.DOTALL|re.I)
               ):
    """
        Return only the portion of 'text' which lies between the
        <body> and </body> tags;  if either is missing, return the
        whole thing.
    """
    body_start = BODYSTART.search(text)
    if not body_start:
        return text

    body_end = BODYEND.search(text)
    if not body_end:
        return text

    return text[ body_start.end() : body_end.start() ]


def _parseSTXHeadersBody( body
                        , headers=None
                        , LINE_SPLIT=re.compile( r'[\n\r]+?' )
                        , COLON_SPLIT=re.compile( r':[ ]*' )
                        ):
    """
        Parse any leading 'RFC-822'-ish headers from an uploaded
        document, returning a dictionary containing the headers
        and the stripped body.

        E.g.::

            Title: Some title
            Creator: Tres Seaver
            Format: text/plain
            X-Text-Format: structured

            Overview

            This document .....

            First Section

            ....


        would be returned as::

            { 'Title' : 'Some title'
            , 'Creator' : 'Tres Seaver'
            , 'Format' : 'text/plain'
            , 'text_format': 'structured'
            }

        as the headers, plus the body, starting with 'Overview' as
        the first line (the intervening blank line is a separator).

        Allow passing initial dictionary as headers.
    """
    # Split the lines apart, taking into account Mac|Unix|Windows endings
    lines = LINE_SPLIT.split( body )

    i = 0
    if headers is None:
        headers = {}
    else:
        headers = headers.copy()

    hdrlist = []
    for line in lines:

        if line and line[-1] == '\r':
            line = line[:-1]

        if not line:
            break

        tokens = COLON_SPLIT.split( line )

        if len( tokens ) > 1:
            hdrlist.append( ( capitalize( tokens[0] )
                            , join( tokens[1:], ': ' )
                            ) )
        elif i == 0:
            return headers, body     # no headers, just return those passed in.

        else:    # continuation
            last, hdrlist = hdrlist[ -1 ], hdrlist[ :-1 ]
            hdrlist.append( ( last[ 0 ]
                            , join( ( last[1], lstrip( line ) ), '\n' )
                            ) )
        i = i + 1

    for hdr in hdrlist:
        headers[ hdr[0] ] = hdr[ 1 ]

    return headers, join( lines[ i+1: ], '\n' )

##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Structured Text Renderer Classes

$Id: stx.py,v 1.3 2004/02/19 19:56:52 philikon Exp $
"""
import re

from zope.structuredtext.document import Document
from zope.structuredtext.html import HTML
from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.app.interfaces.renderer import IStructuredTextSource, IHTMLRenderer

class StructuredTextSource(unicode):
    """Represents Structured Text source code""" 
    implements(IStructuredTextSource)

    def createComment(self, comment, number, user, date):
        "See zope.app.interfaces.renderer.IStructuredTextSource"
        if number == 1:
            return first_comment_template %(number, user, date, comment)
        else:
            return comment_template %(number, user, date, comment)    
    

class StructuredTextToHTMLRenderer(BrowserView):
    """An Adapter to convert from Plain Text to HTML.""" 
    implements(IHTMLRenderer)
    __used_for__ = IStructuredTextSource

    def render(self, context):
        "See zope.app.interfaces.renderer.IHTMLRenderer"
        doc = Document()(str(self.context))
        html = HTML()(doc)

        # strip html & body added by some zope versions
        html = re.sub(
            r'(?sm)^<html.*<body.*?>\n(.*)</body>\n</html>\n',r'\1', html)

        html = html.replace('<p>----------</p>',
                            '<hr class="comments" size="1" NOSHADE>')
        return html


comment_template = '''

Comment #%i by **%s** (%s)

%s'''

first_comment_template = '''

----------

Comment #%i by **%s** (%s)

%s'''

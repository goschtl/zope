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
"""Plain Text Renderer Classes

$Id: plaintext.py,v 1.1 2003/07/31 17:59:36 srichter Exp $
"""
from zope.interface import implements
from zope.app.interfaces.renderer import IPlainTextSource, IHTMLRenderer
from zope.publisher.browser import BrowserView


class PlainTextSource(unicode):
    """Represents Plain Text source code""" 
    implements(IPlainTextSource)

    def createComment(self, comment, number, user, date):
        "See zope.app.interfaces.renderer.IPlainTextSource"
        if number == 1:
            return first_comment_template %(number, user, date, comment)
        else:
            return comment_template %(number, user, date, comment)    
    

class PlainTextToHTMLRenderer(BrowserView):
    """An Adapter to convert from Plain Text to HTML.""" 
    implements(IHTMLRenderer)
    __used_for__ = IPlainTextSource

    def render(self, context):
        "See zope.app.interfaces.renderer.IHTMLRenderer"
        html = self.context.replace('\n', '<br/>\n')
        html = html.replace('----------<br/>',
                            '<hr class="comments" size="1" NOSHADE>')
        return html


comment_template = '''

Comment #%i by %s (%s)
%s'''

first_comment_template = '''
----------

Comment #%i by %s (%s)
%s'''

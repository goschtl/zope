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
"""ReStructured Text Renderer Classes

$Id: rest.py,v 1.1 2003/07/31 17:59:36 srichter Exp $
"""
import re
import docutils.core, docutils.io
from datetime import datetime

from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.app.interfaces.renderer import IReStructuredTextSource, IHTMLRenderer


class ReStructuredTextSource(unicode):
    """Represents Restructured Text source code""" 
    implements(IReStructuredTextSource)

    def createComment(self, comment, number, user, date):
        "See zope.app.interfaces.renderer.IReStructuredTextSource"
        if number == 1:
            return first_comment_template %(number, user, date, comment)
        else:
            return comment_template %(number, user, date, comment)


class ReStructuredTextToHTMLRenderer(BrowserView):
    """An Adapter to convert from Restructured Text to HTML.""" 
    implements(IHTMLRenderer)
    __used_for__ = IReStructuredTextSource

    def render(self, context):
        "See zope.app.interfaces.renderer.IHTMLRenderer"
        # format with strings
        pub = docutils.core.Publisher()
        pub.set_reader('standalone', None, 'restructuredtext')
        pub.set_writer('html')

        # go with the defaults
        pub.get_settings()

        # this is needed, but doesn't seem to do anything
        pub.settings._destination = ''

        # use the Zope 3 stylesheet
        pub.settings.stylesheet = 'zope3.css'

        # set the reporting level to something sane (1 being the smallest)
        pub.settings.report_level = 1

        # don't break if we get errors
        pub.settings.halt_level = 6

        # input
        pub.source = docutils.io.StringInput(source=self.context)

        # output - not that it's needed
        pub.destination = docutils.io.StringOutput(encoding='UTF-8')

        # parse!
        document = pub.reader.read(pub.source, pub.parser, pub.settings)

        # transform
        pub.apply_transforms(document)

        # do the format
        html = pub.writer.write(document, pub.destination)
        html = re.sub(
            r'(?sm)^<\?xml.*<html.*<body.*?>\n(.*)</body>\n</html>\n',r'\1',
            html)
        return html
    

comment_template = '''

Comment #%i by **%s** (%s)

%s'''

first_comment_template = '''
----------

Comment #%i by **%s** (%s)

%s'''

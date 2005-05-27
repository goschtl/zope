##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""ReStructured Text Renderer Classes

$Id$
"""
import docutils.core, docutils.io
from docutils import nodes, writers
from docutils.writers.html4css1 import HTMLTranslator
from docutils.writers.html4css1 import Writer as HTMLWriter

from zope.interface import implements
from zope.app.publisher.browser import BrowserView
from zope.app.renderer.interfaces import ISource, IHTMLRenderer
from zope.app.renderer import SourceFactory


class IReStructuredTextSource(ISource):
    """Marker interface for a restructured text source. Note that an
    implementation of this interface should always derive from unicode or
    behave like a unicode class."""


ReStructuredTextSourceFactory = SourceFactory(IReStructuredTextSource)


class Writer(writers.Writer):
    """
    A custom docutils writer that will ultimately give us
    only a body, utilizing the docutils framework.
    """
    supported = ('html',)
    """ Formats this writer supports."""

    settings_spec = (
        'Zope 3 Specific Options',
        None,
        (('Specify base section (i.e. if 3, a top-level section '
          'would be written as H3, 2nd level H4, etc...).  Default is 3.',
          ['--base-section'],
          {'choices': ['1','2','3','4'], 
            'default': '3', 
            'metavar': '<NUMBER>'}),) + HTMLWriter.settings_spec[2]
        )

    relative_path_settings = ('stylesheet_path',)

    output = None

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = ZopeTranslator

    def translate(self):
        visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()
        self.stylesheet = visitor.stylesheet
        self.body = visitor.body


class ZopeTranslator(HTMLTranslator):
    """
    The ZopeTranslator extends the base HTML processor for reST.  It
    augments reST by:

    - Starting headers at level 3 (this does not apply to the title
      header, which occurs if a reST header element appears as the first
      element in a document).  This generally allows reST HTML code to
      fit in an existing site.

    - Outputs *only* the 'body' parts of the document tree, using the
      internal docutils structure.
    """
    def __init__(self, document):
        document.settings.embed_stylesheet = 0
        document.settings.base_section = int(document.settings.base_section)
        
        HTMLTranslator.__init__(self, document)

    def astext(self):
        """
        This is where we join the document parts that we want in
        the output.
        """
        # use the title, subtitle, author, date, etc., plus the content
        body = self.body_pre_docinfo + self.docinfo + self.body
        return u"".join(body)

    def visit_title(self, node):
        """
        Handles the base section settings (ie - starting the
        document with header level 3)
        """
        if isinstance(node.parent, nodes.topic):
            HTMLTranslator.visit_title(self, node)
        elif self.section_level == 0:
            HTMLTranslator.visit_title(self, node)
        else:
            # offset section level to account for ``base_section``.
            self.section_level += (self.settings.base_section - 1)
            HTMLTranslator.visit_title(self, node)
            self.section_level -= (self.settings.base_section - 1)


class ReStructuredTextToHTMLRenderer(BrowserView):
    r"""An Adapter to convert from Restructured Text to HTML.

    Examples::

      >>> from zope.publisher.browser import TestRequest
      >>> source = ReStructuredTextSourceFactory(u'''
      ... This is source.
      ... 
      ... Header 3
      ... --------
      ... This is more source.
      ... ''')
      >>> renderer = ReStructuredTextToHTMLRenderer(source, TestRequest())

      DISABLED due to differences in reST behavior between
      Zope 2.8 and Zope 3. Consequence of Five integration.
      #>>> print renderer.render().strip()
      #<div class="document">
      #<p>This is source.</p>
      #<div class="section" id="header-3">
      #<h3><a name="header-3">Header 3</a></h3>
      #<p>This is more source.</p>
      #</div>
      #</div>
    """ 


    implements(IHTMLRenderer)
    __used_for__ = IReStructuredTextSource

    def render(self):
        "See zope.app.interfaces.renderer.IHTMLRenderer"
        settings_overrides = {
            'footnote_references': 'brackets',
            'report_level': 1,
            'halt_level': 6,
            'stylesheet': 'zope3.css',
            }
        html = docutils.core.publish_string(
            self.context,
            writer=Writer(),            # Our custom writer
            settings_overrides=settings_overrides,
            )
        return html

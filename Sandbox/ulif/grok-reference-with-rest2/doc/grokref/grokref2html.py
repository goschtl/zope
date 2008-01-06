##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Create the grok reference in various output formats."""

import time

from docutils import nodes
from docutils.core import publish_cmdline, default_description
from docutils.readers.standalone import Reader
from docutils.transforms import Transform
from docutils.transforms.universal import FilterMessages
from docutils.parsers.rst import Parser

from docutils.writers.s5_html import Writer as S5Writer
from docutils.writers.s5_html import S5HTMLTranslator as S5BaseTranslator

from docutils.writers.latex2e import Writer as LaTeX2eWriter

from extensions import directives, roles
from extensions.translators import HTMLTranslator


class AdditionalSubstitutions(Transform):
    default_priority = 210
    def apply(self):
        config = self.document.settings.reference_settings
        for ref in self.document.traverse(nodes.substitution_reference):
            refname = ref['refname']
            text = config.get(refname, None)
            ref.replace_self(nodes.Text(text, text))
        return

class ReferenceReader(Reader):
    def get_transforms(self):
        tf = Reader.get_transforms(self)
        return tf + [AdditionalSubstitutions, FilterMessages]


class ReferenceParser(Parser):
    pass

class ReferenceTranslatorS5(S5BaseTranslator, HTMLTranslator):
    def __init__(self, *args, **kwds):
        S5BaseTranslator.__init__(self, *args, **kwds)
        self.highlightlang = 'python'

    def unknown_visit(self, node):
        print "UNKNOWN: ", node
    def unknown_departure(self, node):
        pass

class ReferenceS5Writer(S5Writer):
    def __init__(self, *args, **kw):
        S5Writer.__init__(self)
        self.translator_class = ReferenceTranslatorS5


class ReferenceLaTeX2eWriter(LaTeX2eWriter):
    pass


class ReferenceProducer(object):
    """
    """

    settings = {
        'filename': None,
        'today': '01/01/1970',
        'version': 'None',
        'release': 'unknown'
        }

    description = ('Generates reference documents from standalone '
                   'reStructuredText sources.  ' + default_description)        

    def __init__(self, filename=None):
        self.reader = ReferenceReader()
        self.parser = ReferenceParser()
        self.writer = ReferenceS5Writer()
        # Values from the `settings` directory can be used as
        # substituted values in documents.  For example it is possible
        # to use |foo| and this term will be substituted by a value
        # defined in self.settings, called `foo`.  If such a key does
        # not exist, a warning will be generated.  This requires a
        # reader of type 'ReferenceReader'.
        self.settings = {
            'filename': filename,
            'today': time.strftime('%B %d, %Y'),
            'version': 'foo',
            'release': 'bar'
            }

    def publish(self):
        """Generate the reference."""
        settings_overrides = {
            'halt_level': 6,
            'input_encoding': 'utf8',
            'output_encoding': 'utf8',
            'initial_header_level': 2,
            # don't try to include the stylesheet (docutils gets hiccups)
            'stylesheet_path': '',
            'reference_settings' : self.settings,
        }
        publish_cmdline(
            reader=self.reader,
            writer=self.writer,
            parser=self.parser,
            description=self.description,
            settings_overrides=settings_overrides
            )
        

def main():
    reference = ReferenceProducer().publish()

if __name__ == '__main__':
    main()

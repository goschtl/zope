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

import os
import sys
import codecs

import docutils.core
#from docutils import nodes
from docutils.writers.html4css1 import Writer

from grokref.translators import HTMLTranslator
from grokref.extensions import addnodes, roles, directives

#from zope.app.renderer.rest import ZopeTranslator

class ReStructuredTextToHTMLRenderer:
    """Convert from Restructured Text to HTML."""

    def __init__(self, content):
        self.content = content

    def render(self):
        settings_overrides = {
            'halt_level': 6,
            'input_encoding': 'utf8',
            'output_encoding': 'utf8',
            'initial_header_level': 2,
            # don't try to include the stylesheet (docutils gets hiccups)
            'stylesheet_path': '',
        }

        #docutils.nodes._add_node_class_names('desc')
        writer = Writer()
        #print docutils.nodes
        #writer.translator_class = ZopeTranslator
        writer.translator_class = HTMLTranslator
        html = docutils.core.publish_string(
                        self.content,
                        writer=writer,
                        settings_overrides=settings_overrides,)
        html = codecs.decode(html, 'utf_8')
        return html


class ReSTFile(object):
    source_text = None
    file_path = None

    def __init__(self, filename=None):
        self.source_text = codecs.open(filename, "r", 'utf-8').read()
        self.file_path = filename

    def getHTML(self):
        return ReStructuredTextToHTMLRenderer(self.source_text).render()
        

def getRestFiles(filepath):
    if os.path.isdir(filepath):
        return [os.path.join(filepath, filename)
                for filename in os.listdir(filepath)
                if filename.endswith('.rst')]
    return [filepath]

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    
    if not len(argv):
        print "Usage: %s REFDIR|FILE" % (sys.argv[0])
        sys.exit(1)

    if not os.path.isdir(argv[0]) and not os.path.isfile(argv[0]):
        print "%s: No such file or directory" % (argv[0])
        sys.exit(1)

    rest_files = getRestFiles(argv[0])
    print "files: ", rest_files

    print "Content: "
    for filename in rest_files:
        print ReSTFile(filename).getHTML()

    
if __name__ == '__main__':
    main()

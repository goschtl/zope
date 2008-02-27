# -*- coding: utf-8 -*-
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
"""Build grok authorative documentaion.
"""
import sys
import os.path
from shutil import copyfile
import getopt
from docutils import nodes
from docutils.parsers.rst import directives
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import LatexFormatter
from ulif.rest import pygments_directive
import sphinx
from sphinx.util.console import nocolor
from sphinx.latexwriter import LaTeXTranslator

HERE = os.path.dirname(__file__)

SRCDIR_ALL = os.path.dirname(os.path.dirname(__file__))
SRCDIR_REF = os.path.join(SRCDIR_ALL, 'reference')

HTMLDIR_ALL = os.path.join(HERE, 'html')
HTMLDIR_REF = os.path.join(HERE, 'html', 'reference')

LATEX_ALL = os.path.join(HERE, 'latex')


def simple_directive(
    name, arguments, options, content, lineno,
    content_offset, block_text, state, state_machine):
    """A docutils directive, that feeds content as literal block.

    This is needed to circumvent highlighting quirks when doing
    non-HTML output. The pygments_directive delivers plain HTML, which
    we must avoid when generating LaTeX for example.
    """
    return [nodes.literal_block('', '\n'.join(content), options=options)]

simple_directive.arguments = (1, 0, 1)
simple_directive.content = 1


LATEX_SETTINGS = {
    'DEFAULT': LatexFormatter(),
    'VARIANTS' : {
       'linenos' : LatexFormatter(linenos=True),
       'nolinenos' : LatexFormatter(linenos=False)
       },
    'FORMAT': 'latex',
    }

def pygments_latex_directive(name, arguments, options, content, lineno,
                             content_offset, block_text, state, state_machine):
    """A docutils directive that provides syntax highlighting for LaTeX.

    This is needed to circumvent highlighting quirks when doing
    non-HTML output. The pygments_directive delivers plain HTML, which
    we must avoid when generating LaTeX for example.
    """
    try:
        lexer = get_lexer_by_name(arguments[0])
    except ValueError:
        # no lexer found - use the text one instead of an exception
        lexer = TextLexer()
    # take an arbitrary option if more than one is given
    formatter = options and LATEX_SETTINGS['VARIANTS'][
        options.keys()[0]] or LATEX_SETTINGS['DEFAULT']
    parsed = highlight(u'\n'.join(content), lexer, formatter)
    return [nodes.raw('', parsed, format=LATEX_SETTINGS['FORMAT'])]

pygments_latex_directive.arguments = (1, 0, 1)
pygments_latex_directive.content = 1



def usage(argv, msg=None, default_src=None, default_out=None):
    """Some hints for users.

    Adapted from sphinx __init__. Because we add an `-h` option and
    provide a slightliy different syntax than stock sphinx (srcdir and
    targetdir have defaults here), we also need our own help texts.
    """

    if msg:
        print >>sys.stderr, msg
        print >>sys.stderr
    print >>sys.stderr, """\
usage: %s [options] [sourcedir [outdir [filenames...]]]
options: -b <builder> -- builder to use; default is html
         -a        -- write all files; default is to only write new and changed files
         -E        -- don't use a saved environment, always read all files
         -d <path> -- path for the cached environment and doctree files
                      (default outdir/.doctrees)
         -D <setting=value> -- override a setting in sourcedir/conf.py
         -N        -- do not do colored output
         -q        -- no output on stdout, just warnings on stderr
         -P        -- run Pdb on exception
         -h        -- print this help

default sourcedir is %s
default outputdir is %s

modi:
* without -a and without filenames, write new and changed files.
* with -a, write all files.
* with filenames, write these.""" % (argv[0],default_src, default_out)

def usage_grokdoc(argv, msg=None):
    """Wrapper that displays source and target of all docs.
    """
    return usage(argv, msg=msg, default_src=SRCDIR_ALL,
                 default_out=HTMLDIR_ALL)

def usage_grokref(argv, msg=None):
    """Wrapper that displays source and target of reference docs.
    """
    return usage(argv, msg=msg, default_src=SRCDIR_REF,
                 default_out=HTMLDIR_REF)


def grokdocs(argv=sys.argv, srcdir=SRCDIR_ALL, htmldir=HTMLDIR_ALL,
             latexdir=LATEX_ALL):
    """Generate the whole docs, including howtos, reference, etc.
    """
    if srcdir == SRCDIR_ALL:
        sphinx.usage = usage_grokdoc
    print "SRCDIR", srcdir
    if not sys.stdout.isatty() or sys.platform == 'win32':
        # Windows' poor cmd box doesn't understand ANSI sequences
        nocolor()
    opts, args = None, None
    try:
        opts, args = getopt.getopt(argv[1:], 'ab:d:D:NEqPh')
    except getopt.error:
        # sphinx will handle that errors
        pass

    if len(args) < 1:
        argv.append(srcdir)
    if len(args) < 2:
        argv.append(htmldir)

    if opts and '-h' in [x for x,y in opts]:
        sphinx.usage(argv, msg=None)
        return 1

    if opts and '-b' in [x for x,y in opts]:
        val = filter(lambda x: x[0] == '-b', opts)
        val = val[0][1]
        if val == 'latex':
            # disable code-block directive by substituting it with a
            # LaTeX-specialized version...
            directives.register_directive('sourcecode',
                                          pygments_latex_directive)
            directives.register_directive('code-block',
                                          pygments_latex_directive)
            # Inject a translator handler for raw text (sphinx lacks
            # one by default).
            def visit_raw(self, node):
                if 'latex' in node.get('format', '').split():
                    self.body.append(r'%s' % node.astext())
                raise nodes.SkipNode
            LaTeXTranslator.visit_raw = visit_raw

            # Inject a working pygments workaround.
            def depart_literal_block(self, node):
                hlcode = self.highlighter.highlight_block(self.verbatim.rstrip(
                    '\n'), self.highlightlang)
                # workaround for Unicode issue
                hlcode = hlcode.replace(u'€', u'@texteuro[]')
                # workaround for Pygments bug
                hlcode = hlcode.replace('\\end{Verbatim}',
                                        '\n\\end{Verbatim}')
                self.body.append('\n' + hlcode)
                self.verbatim = None
            LaTeXTranslator.depart_literal_block = depart_literal_block
            LaTeXTranslator.depart_doctest_block = depart_literal_block
            
            # Inject a more correct topic handler (sphinx default
            # handler fails to handle verbatim environments in
            # topics/sidebars.
            def visit_topic(self, node):
                self.body.append('\\setbox0\\vbox{\n'
                                 '\\begin{minipage}{0.75\\textwidth}\n')
            def depart_topic(self, node):
                self.body.append('\\end{minipage}}\n'
                                 '\\begin{center}\\setlength{\\fboxsep}{5pt}'
                                 '\\shadowbox{\\box0}\\end{center}\n')
            LaTeXTranslator.visit_topic = visit_topic
            LaTeXTranslator.depart_topic = depart_topic
            LaTeXTranslator.visit_sidebar = visit_topic
            LaTeXTranslator.depart_sidebar = depart_topic

            def visit_image(self, node):
                attrs = node.attributes
                # Add image URI to dependency list, assuming that it's
                # referring to a local file.
                #self.settings.record_dependencies.add(attrs['uri'])
                pre = []                        # in reverse order
                post = []
                include_graphics_options = ""
                inline = isinstance(node.parent, nodes.TextElement)
                if attrs.has_key('scale'):
                    # Could also be done with ``scale`` option to
                    # ``\includegraphics``; doing it this way for consistency.
                    pre.append('\\scalebox{%f}{' % (attrs['scale'] / 100.0,))
                    post.append('}')
                if attrs.has_key('width'):
                    include_graphics_options = '[width=%s]' % attrs['width']
                if attrs.has_key('align'):
                    align_prepost = {
                        # By default latex aligns the top of an image.
                        (1, 'top'): ('', ''),
                        (1, 'middle'): ('\\raisebox{-0.5\\height}{', '}'),
                        (1, 'bottom'): ('\\raisebox{-\\height}{', '}'),
                        (0, 'center'): ('{\\hfill', '\\hfill}'),
                        # These 2 don't exactly do the right thing.
                        # The image should be floated alongside the
                        # paragraph.  See
                        # http://www.w3.org/TR/html4/struct/objects.html#adef-align-IMG
                        (0, 'left'): ('{', '\\hfill}'),
                        (0, 'right'): ('{\\hfill', '}'),}
                    try:
                        pre.append(align_prepost[inline, attrs['align']][0])
                        post.append(align_prepost[inline, attrs['align']][1])
                    except KeyError:
                        pass                    # XXX complain here?
                if not inline:
                    pre.append('\n')
                    post.append('\n')
                    pre.reverse()
                    self.body.extend( pre )
                    self.body.append( '\\includegraphics%s{%s}' % (
                        include_graphics_options, attrs['uri'] ) )
                    self.body.extend( post )
            def depart_image(self, node):
                pass

            LaTeXTranslator.visit_image = visit_image
            LaTeXTranslator.depart_image = depart_image

            # Set default sourcedir...
            if len(args) < 2:
                argv[-1] = latexdir
            # Copy fncychap.sty to targetdir...
            if os.path.isdir(argv[-1]):
                copyfile(os.path.join(HERE, 'texinputs', 'fncychap.sty'),
                         os.path.join(argv[-1], 'fncychap.sty'))
            
    args = argv                 

    print "Source directory is: ", argv[-2]
    print "Target directory is: ", argv[-1]
    print "(run `%s -h` to see the options available)" % argv[0]

    sphinx.main(argv)

    print "Generated docs are in %s." % os.path.abspath(argv[-1])


def grokref(argv=sys.argv):
    """Generate the reference docs.
    """
    sphinx.usage = usage_grokref
    return grokdocs(argv, srcdir=SRCDIR_REF, htmldir=HTMLDIR_REF,
                    latexdir=LATEX_ALL)

def sphinxquickstart(argv=sys.argv):
    from sphinx import quickstart
    quickstart.main(argv)


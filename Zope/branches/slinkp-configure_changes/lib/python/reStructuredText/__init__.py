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
"""Wrapper to integrate reStructuredText into Zope

This implementation requires docutils 0.3.4+ from http://docutils.sf.net/
"""

import sys, os, locale
from App.config import getConfiguration
from docutils.core import publish_parts

# get encoding
default_enc = sys.getdefaultencoding()
default_output_encoding = getConfiguration().rest_output_encoding or default_enc
default_input_encoding = getConfiguration().rest_input_encoding or default_enc

# starting level for <H> elements (default behaviour inside Zope is <H3>)
default_level = 3
initial_header_level = getConfiguration().rest_header_level or default_level

# default language
default_lang = getConfiguration().locale or locale.getdefaultlocale()[0]
if default_lang and '_' in default_lang:
    default_lang = default_lang[:default_lang.index('_')]


class Warnings:

    def __init__(self):
        self.messages = []

    def write(self, message):
        self.messages.append(message)

def render(src,
           writer='html4css1',
           report_level=1,
           stylesheet='default.css',
           input_encoding=default_input_encoding,
           output_encoding=default_output_encoding,
           language_code=default_lang,
           initial_header_level = initial_header_level,
           settings = {}):
    """get the rendered parts of the document the and warning object
    """
    # Docutils settings:
    settings = settings.copy()
    settings['input_encoding'] = input_encoding
    settings['output_encoding'] = output_encoding
    settings['stylesheet'] = stylesheet
    settings['language_code'] = language_code
    # starting level for <H> elements:
    settings['initial_header_level'] = initial_header_level
    # set the reporting level to something sane:
    settings['report_level'] = report_level
    # don't break if we get errors:
    settings['halt_level'] = 6
    # remember warnings:
    settings['warning_stream'] = warning_stream = Warnings()

    parts = publish_parts(source=src, writer_name=writer,
                          settings_overrides=settings,
                          config_section='zope application')

    return parts, warning_stream

def HTML(src,
         writer='html4css1',
         report_level=1,
         stylesheet='default.css',
         input_encoding=default_input_encoding,
         output_encoding=default_output_encoding,
         language_code=default_lang,
         initial_header_level = initial_header_level,
         warnings = None,
         settings = {}):
    """ render HTML from a reStructuredText string 

        - 'src'  -- string containing a valid reST document

        - 'writer' -- docutils writer 

        - 'report_level' - verbosity of reST parser

        - 'stylesheet' - Stylesheet to be used

        - 'input_encoding' - encoding of the reST input string

        - 'output_encoding' - encoding of the rendered HTML output
        
        - 'report_level' - verbosity of reST parser

        - 'language_code' - docutils language
        
        - 'initial_header_level' - level of the first header tag
        
        - 'warnings' - will be overwritten with a string containing the warnings
        
        - 'settings' - dict of settings to pass in to Docutils, with priority

    """
    parts, warning_stream = render(src,
                                   writer = writer,
                                   report_level = report_level,
                                   stylesheet = stylesheet,
                                   input_encoding = input_encoding,
                                   output_encoding = output_encoding,
                                   language_code=language_code,
                                   initial_header_level = initial_header_level,
                                   settings = settings)

    output = ('<h%(level)s class="title">%(title)s</h%(level)s>\n'
              '%(docinfo)s%(body)s' % {
                  'level': initial_header_level,
                  'title': parts['title'],
                  'docinfo': parts['docinfo'],
                  'body': parts['body']
              }).encode(output_encoding)

    warnings = ''.join(warning_stream.messages)

    return output


__all__ = ("HTML", 'render')

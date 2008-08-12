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
"""Helpers for the zope.introspectorui.
"""
import re
import grokcore.component as grok
from zope.introspectorui.interfaces import IBreadcrumbProvider, ICodeView
from zope.introspector.code import Code, Package

_format_dict = {
    'plaintext': 'zope.source.plaintext',
    'structuredtext': 'zope.source.stx',
    'restructuredtext': 'zope.source.rest'
    }

space_re = re.compile('\n^( *)\S', re.M)

class CodeBreadcrumbProvider(grok.Adapter):
    """An adapter, that adapts 'ICodeView' objects, i.e. all views
    defined in the ``code`` module.
    """
    grok.context(ICodeView)
    grok.provides(IBreadcrumbProvider)

    def getBreadcrumbs(self):
        code_obj = self.context.context.context
        parts = []
        while getattr(code_obj, '__parent__', None):
            parts.append(code_obj)
            if isinstance(code_obj, Package) and not isinstance(
                code_obj.__parent__, Package):
                break
            code_obj = code_obj.__parent__
        parts.reverse()
        result = ['<a href="%s">%s</a>' % (self.context.url(x), x.__name__)
                  for x in parts]
        return '.'.join(result)

def get_doc_format(module):
    """Convert a module's __docformat__ specification to a renderer source
    id"""
    format = getattr(module, '__docformat__', 'restructuredtext').lower()
    # The format can also contain the language, so just get the first part
    format = format.split(' ')[0]
    return _format_dict.get(format, 'zope.source.rest')

def dedent_string(text):
    """Dedent the docstring, so that docutils can correctly render it."""
    dedent = min([len(match) for match in space_re.findall(text)] or [0])
    return re.compile('\n {%i}' % dedent, re.M).sub('\n', text)

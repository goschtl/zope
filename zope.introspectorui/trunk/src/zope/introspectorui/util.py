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


class CodeBreadcrumbProvider(grok.Adapter):
    """An adapter, that adapts 'ICodeView' objects, i.e. all views
    defined in the ``code`` module.
    """
    grok.context(ICodeView)
    grok.provides(IBreadcrumbProvider)

    def getBreadcrumbs(self):
        code_obj = self.context.context.context
        dotted_name = code_obj.dotted_name
        if hasattr(code_obj, 'name'):
            dotted_name += '.' + code_obj.name
        parts = []
        while code_obj.__parent__:
            parts.append(code_obj)
            curr_dotted_name = '.'.join([x.__name__ for x in parts])
            code_obj = code_obj.__parent__
            if len(curr_dotted_name) >= len(dotted_name):
                break
        parts.reverse()
        result = ['<a href="%s">%s</a>' % (self.context.url(x), x.__name__)
                  for x in parts]
        return '.'.join(result)

def get_doc_format(module):
    """Convert a module's __docformat__ specification to a renderer source
    id"""
    format = getattr(module, '__docformat__', 'plaintext').lower()
    # The format can also contain the language, so just get the first part
    format = format.split(' ')[0]
    return _format_dict.get(format, 'zope.source.plaintext')

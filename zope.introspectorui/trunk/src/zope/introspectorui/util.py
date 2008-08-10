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
import grokcore.component as grok
from zope.introspectorui.interfaces import IBreadcrumbProvider, ICodeView
from zope.introspector.code import Code, Package

class CodeBreadcrumbProvider(grok.Adapter):
    """An adapter, that adapts 'ICodeView' objects, i.e. all views
    defined in the ``code`` module.
    """
    grok.context(ICodeView)
    grok.provides(IBreadcrumbProvider)

    def getBreadcrumbs(self):
        code_obj = self.context.context.context
        items = code_obj.getParents()
        result = []
        for item in items:
            name = getattr(item, 'name', item.dotted_name.split('.')[-1])
            url = self.context.url(item)
            result.append(
                '<a href="%s">%s</a>' % (url, name))
        return '.'.join(result)

##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""File-based page templates that can be used as methods on views.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from z3c.mvc import interfaces
from z3c.template.macro import Macro

class ModelTemplate(ViewPageTemplateFile):
    """Page Template that only has access to a well defined model
    """
    implements(interfaces.IModelTemplate)

    def pt_getContext(self, instance, request, **_kw):
        # instance is a View component
        namespace = super(ViewPageTemplateFile, self).pt_getContext(**_kw)
        assert interfaces.IModelProvider.providedBy(instance)
        namespace['model'] = instance.getModel()
        return namespace


class TemplateFactory(object):
    """Template factory."""

    template = None

    def __init__(self, filename, contentType, macro=None):
        self.macro = macro
        self.contentType = contentType
        self.template = ModelTemplate(filename, content_type=contentType)

    def __call__(self, view, request):
        if self.macro is None:
            return self.template
        return Macro(self.template, self.macro, view, request,
            self.contentType)

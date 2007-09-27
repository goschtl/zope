##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""
$Id$
"""

import zope.component
from zope.pagetemplate.interfaces import IPageTemplate
from zope.app.pagetemplate import ViewPageTemplateFile

from z3c.template import interfaces
from z3c.template.macro import Macro


class TemplateFactory(object):
    """Template factory."""

    template = None

    def __init__(self, filename, contentType, macro=None):
        self.macro = macro
        self.contentType = contentType
        self.template = ViewPageTemplateFile(filename,
            content_type=contentType)

    def __call__(self, view, request):
        if self.macro is None:
            return self.template
        return Macro(self.template, self.macro, view, request,
            self.contentType)


class BoundViewTemplate(object):
    def __init__(self, pt, ob):
        object.__setattr__(self, 'im_func', pt)
        object.__setattr__(self, 'im_self', ob)

    def __call__(self, *args, **kw):
        if self.im_self is None:
            im_self, args = args[0], args[1:]
        else:
            im_self = self.im_self
        return self.im_func(im_self, *args, **kw)

    def __setattr__(self, name, v):
        raise AttributeError("Can't set attribute", name)

    def __repr__(self):
        return "<BoundViewTemplate of %r>" % self.im_self


class ViewTemplate(object):

    def __init__(self, provides=IPageTemplate, name=u''):
        self.provides = provides
        self.name = name

    def __call__(self, instance, *args, **keywords):
        template = zope.component.getMultiAdapter(
                (instance, instance.request), self.provides, name=self.name)
        return template(instance, *args, **keywords)

    def __get__(self, instance, type):
        return BoundViewTemplate(self, instance)

getViewTemplate = ViewTemplate


class GetPageTemplate(ViewTemplate):

    def __init__(self, name=u''):
        self.provides = interfaces.IContentTemplate
        self.name = name

getPageTemplate = GetPageTemplate


class GetLayoutTemplate(ViewTemplate):

    def __init__(self, name=u''):
        self.provides = interfaces.ILayoutTemplate
        self.name = name

getLayoutTemplate = GetLayoutTemplate

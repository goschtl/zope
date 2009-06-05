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

from z3c.pt.pagetemplate import ViewPageTemplate as Z3CViewPageTemplate
from z3c.pt.pagetemplate import PageTemplateFile as Z3CPageTemplateFile
from grokcore.view.components import PageTemplate as BasePageTemplate
import martian

import sys
import os.path

class ViewPageTemplate(Z3CViewPageTemplate):
    """Grok let users define their namespace.
    """

    def _pt_get_context(self, view, request, kwargs):
        default = kwargs.get('default_namespace', None)
        if default:
            del kwargs['default_namespace']
        parameters = dict(
            view=view,
            context=view.context,
            request=request or view.request,
            template=self,
            options=kwargs,
            nothing=None)
        if default:
            parameters.update(default)
        return parameters


class ViewPageTemplateFile(ViewPageTemplate, Z3CPageTemplateFile):
    """Let grok user defines their namespace.
    """


class PageTemplate(BasePageTemplate):
    """A Grok z3c.pt template based.
    """

    def setFromString(self, string):
        self._template = ViewPageTemplate(string)

    def setFromFilename(self, filename, _prefix=None):
        self._template = ViewPageTemplateFile(filename, _prefix)

    def _initFactory(self, factory):
        pass

    def render(self, view):
        namespace = self.getNamespace(view)
        return self._template(view, default_namespace=namespace)


class PageTemplateFile(PageTemplate):
    """A Grok Page template file.
    """
    # For BBB
    def __init__(self, filename, _prefix=None):
        self.__grok_module__ = martian.util.caller_module()
        if _prefix is None:
            module = sys.modules[self.__grok_module__]
            _prefix = os.path.dirname(module.__file__)
        self.setFromFilename(filename, _prefix)

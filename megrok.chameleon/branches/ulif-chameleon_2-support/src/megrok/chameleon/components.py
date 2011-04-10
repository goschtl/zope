##############################################################################
#
# Copyright (c) 2006-2009 Zope Foundation and Contributors.
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
"""Chameleon page template components"""
import os
from chameleon.zpt.template import PageTemplateFile, PageTemplate
from chameleon.genshi.template import (GenshiTemplateFile, GenshiTemplate,
                                       GenshiTextTemplateFile,
                                       GenshiTextTemplate)
from grokcore.component import GlobalUtility, implements, name
from grokcore.view import interfaces
from grokcore.view.components import GrokTemplate

#
# Chameleon Zope Page Templates...
#
class ChameleonPageTemplate(GrokTemplate):

    def setFromString(self, string):
        self._filename = None
        self._template = PageTemplate(string)

    def setFromFilename(self, filename, _prefix=None):
        self._filename = filename
        self._prefix = _prefix
        self._template = PageTemplateFile(os.path.join(_prefix, filename))
        return

    def getNamespace(self, view):
        """Extend namespace.

        Beside the vars defined in standard grok templates, we inject
        some vars and functions to be more compatible with official
        ZPTs.
        """
        namespace = super(ChameleonPageTemplate, self).getNamespace(view)
        namespace.update(dict(
                template=self,
                nothing=None,
                ))                
        return namespace

    @property
    def macros(self):
        return self._template.macros

    def render(self, view):
        return self._template(**self.getNamespace(view))

class ChameleonPageTemplateFactory(GlobalUtility):
    implements(interfaces.ITemplateFileFactory)
    name('cpt')

    def __call__(self, filename, _prefix=None):
        return ChameleonPageTemplate(filename=filename, _prefix=_prefix)

#
# Chameleon Genshi Templates
#
class ChameleonGenshiTemplate(GrokTemplate):
    filename = None
    _format = None

    def setFromString(self, string):
        self._filename = None
        self._template = GenshiTemplate(string, format=self._format)

    def setFromFilename(self, filename, _prefix=None):
        self._filename = filename
        self._prefix = _prefix
        self._template = GenshiTemplateFile(
            os.path.join(_prefix, filename), format=self._format)
        return

    def render(self, view):
        if self._filename is not None:
            self.setFromFilename(self._filename, self._prefix)
        return self._template(**self.getNamespace(view))

class ChameleonGenshiTemplateFactory(GlobalUtility):
    implements(interfaces.ITemplateFileFactory)
    name('cg')

    def __call__(self, filename, _prefix=None):
        return ChameleonGenshiTemplate(filename=filename, _prefix=_prefix)


class ChameleonGenshiTextTemplate(GrokTemplate):
    filename = None

    def setFromString(self, string):
        self._filename = None
        self._template = GenshiTextTemplate(string)

    def setFromFilename(self, filename, _prefix=None):
        self._filename = filename
        self._prefix = _prefix
        self._template = GenshiTextTemplateFile(
            os.path.join(_prefix, filename))
        return

    def render(self, view):
        if self._filename is not None:
            self.setFromFilename(self._filename, self._prefix)
        return self._template(**self.getNamespace(view))

class ChameleonGenshiTextTemplateFactory(GlobalUtility):
    implements(interfaces.ITemplateFileFactory)
    name('cgt')

    def __call__(self, filename, _prefix=None):
        return ChameleonGenshiTextTemplate(filename=filename, _prefix=_prefix)

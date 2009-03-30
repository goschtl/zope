##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
import zope.interface
import os
import grok
from grokcore.view.components import GrokTemplate
from grokcore.view.interfaces import ITemplateFileFactory
from Cheetah.Template import Template 
from imp import new_module, load_source

# Cheetah, by default, automatically calls callables found within the 
# namespace passed to it. Since the namespace contains the view itself,
# the result is a circular calling race condition.
COMPILER_SETTINGS = {'useAutocalling': False}
class CheetahTemplate(GrokTemplate):
    def setFromString(self, string):
        self._template = Template.compile(string, 
                                          compilerSettings=COMPILER_SETTINGS,
                                          )
    def setFromFilename(self, filename, _prefix=None):
        file = open(os.path.join(_prefix, filename))
        self._template = Template.compile(file=file, 
                                          compilerSettings=COMPILER_SETTINGS,
                                          )
    def render(self, view):
        return self._template(namespaces=self.getNamespace(view)).respond()

class CheetahTemplateFactory(grok.GlobalUtility):
    grok.implements(ITemplateFileFactory)
    grok.name('tmpl')

    def __call__(self, filename, _prefix=None):
        return CheetahTemplate(filename=filename, _prefix=_prefix)

import sys
# Since cheetah templates are loaded as modules we create a separate 
# namespace for them to avold collisions.
CHEETAH_NS = 'megrok.cheetah.ns'
sys.modules[CHEETAH_NS] = new_module(CHEETAH_NS)
class CompiledCheetahTemplate(GrokTemplate):
    def setFromFilename(self, filename, _prefix=None):
        template_name = os.path.basename(filename).split('.')[0]
        compiled_module = load_source(CHEETAH_NS + '.' + template_name,
                          os.path.join(_prefix, filename))
        self._template = getattr(compiled_module, template_name)

    def render(self, view):
        return self._template(namespaces=self.getNamespace(view)).respond()

class CompiledCheetahTemplateFactory(grok.GlobalUtility):
    grok.implements(ITemplateFileFactory)
    grok.name('ctmpl')

    def __call__(self, filename, _prefix=None):
        return CompiledCheetahTemplate(filename=filename, _prefix=_prefix)

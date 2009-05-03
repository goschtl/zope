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

from jinja2 import Environment, FileSystemLoader
from extensions import translator, _translator_alias, _get_content_provider

import yaml, simplejson, os

from grokcore.component import GlobalUtility, implements, name

from grokcore.view.components import GrokTemplate
from grokcore.view.interfaces import ITemplate, ITemplateFileFactory

from zope.app.applicationcontrol.runtimeinfo import RuntimeInfo
# Create an Environment instance with the i18n extension
# and the FileSystemLoader class loader that will look for
# absolute path templates.

#XXX passing in a None value here is a hack.
#in_dev_mode = RuntimeInfo(None).getDeveloperMode() == 'On'
# Didn't work as expected. We use auto_reload=True by now.
env = Environment(extensions=['jinja2.ext.i18n'],
                  loader=FileSystemLoader('/'))

#Just set the functions used to resolve translations and
#contents providers instead of full Extension classes
env.globals['_'] = _translator_alias
env.globals.update(gettext=translator)
env.globals['provider'] = _get_content_provider

class JTemplate(object):
    """
    Base class for JinjaTemplate and JsonTemplate
    """
    filepath = ''

    @property
    def template(self):
        if self.filepath:
            self._template = env.get_template(self.filepath)

        return self._template

    def setFromString(self, string):
        self._template = env.from_string(string)

    def setFromFilename(self, filename, _prefix=None):
        self.filepath = os.path.join(_prefix, filename)

class JsonTemplate(JTemplate, GrokTemplate):
    implements(ITemplate)

    def render(self, view):
        jinja_render = self.template.render(**self.getNamespace(view))
        yaml_loader = yaml.load(jinja_render)
        return simplejson.dumps(yaml_loader)

class JsonTemplateFactory(GlobalUtility):

    implements(ITemplateFileFactory)
    name('json')

    def __call__(self, filename, _prefix=None):
        return JsonTemplate(filename=filename, _prefix=_prefix)

class JinjaTemplate(JTemplate, GrokTemplate):
    implements(ITemplate)

    def render(self, view):
        return self.template.render(**self.getNamespace(view))

class JinjaTemplateFactory(GlobalUtility):

    implements(ITemplateFileFactory)
    name('jinja')

    def __call__(self, filename, _prefix=None):
        return JinjaTemplate(filename=filename, _prefix=_prefix)

##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""ExtJS Component representation.

$Id$
"""
__docformat__ = "reStructuredText"
import sys
from rwproperty import getproperty, setproperty

import zope.interface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
from zope.pagetemplate.interfaces import IPageTemplate
from zope.schema.fieldproperty import FieldProperty
from zope.security.proxy import removeSecurityProxy

import z3c.form.form
from z3c.form.button import Button, Buttons
from z3c.form.button import ButtonAction
from z3c.form.button import ButtonAction
from z3c.form.interfaces import IFormLayer
from z3c.form.util import SelectionManager
from z3c.formjs.ajax import AJAXHandler, AJAXHandlers
from z3c.formjs.ajax import AJAXRequestHandler
from z3c.pagelet.browser import BrowserPagelet

from z3c.formext import interfaces
from z3c.formext.jsoncompat import jsonEncode


class JSProperties(SelectionManager):
    """JSProperties selection manager."""
    zope.interface.implements(interfaces.IJSProperties)
    managerInterface = interfaces.IJSProperties

    def __init__(self, *args):
        super(JSProperties, self).__init__()
        for arg in args:
            if self.managerInterface.providedBy(arg):
                for name, prop in arg.items():
                    self._data_keys.append(name)
                    self._data_values.append(prop)
                    self._data[name] = prop
            else:
                self._data_keys.append(arg.__name__)
                self._data_values.append(arg)
                self._data[arg.__name__] = arg


def jsproperty(func):
    frame = sys._getframe(1)
    properties = frame.f_locals.setdefault('jsproperties', JSProperties())
    frame.f_locals['jsproperties'] += JSProperties(func)
    return frame.f_locals['jsproperties'][func.__name__]


def dependencyWrap(dep):
    return ('z3c.formext.ModuleLoader.load(\n'
            '  "%s",\n'
            '  function(){\n'
            '    %%s\n'
            '  });' % dep)

class ScriptProvider(object):

    script = ''
    scriptDependencies = ()

    @property
    def scriptTag(self):
        tagWrap = '<script type="text/javascript" language="Javascript">\n%s\n</script>'
        closureWrap = '  (function(){\n%s\n})();'

        depWraps = '%s'
        for dep in self.scriptDependencies:
            depWraps = depWraps % dependencyWrap(dep)

        script = self.script
        if hasattr(script, '__call__'):
            #this is a page template.
            script = script()

        jsVars = ''
        if hasattr(self, 'jsproperties'):
            jsVars = '\n'.join(['    var %s=%s;' % (name, jsonEncode(prop(self)))
                                for name, prop in self.jsproperties.items()])

        return tagWrap % (closureWrap % (depWraps % ('%s\n%s' % (jsVars, script))))


class ScriptPagelet(ScriptProvider, AJAXRequestHandler, BrowserPagelet):
    """A class that can be extended to get all this functionality."""


class ExtJSForm(ScriptProvider, AJAXRequestHandler, z3c.form.form.Form):
    zope.interface.implements(interfaces.IExtJSForm)
    jsonResponse = None

    script = ViewPageTemplateFile('resources/form-script.js')

    @jsproperty
    def config(self):
        return interfaces.IExtJSComponent(self).getConfig()

    @property
    def response(self):
        return jsonEncode(self.jsonResponse or dict(success=True))

    def addFormError(self, error):
        self.jsonResponse['success'] = False
        self.jsonResponse.setdefault('formErrors', [])
        if isinstance(error, unicode):
            error = translate(error)
        self.jsonResponse['formErrors'].append(str(error))

    def extractData(self):
        data, errors = super(ExtJSForm, self).extractData()
        self.jsonResponse = dict(success=True)
        if errors:
            self.jsonResponse = dict(
                success=False,
                # I shouldn't need the below security proxy
                errors={},
                formErrors=[])
            for error in errors:
                error = removeSecurityProxy(error)
                message = translate(error.message)
                if error.widget:
                    self.jsonResponse['errors'][error.widget.id] = message
                else:
                    self.jsonResponse['formErrors'].append(message)
        return data, errors


class ClientButton(Button):
    zope.interface.implements(interfaces.IClientButton)

    success = FieldProperty(interfaces.IClientButton['success'])
    failure = FieldProperty(interfaces.IClientButton['failure'])

    def __init__(self, *args, **kwargs):
        self.success = kwargs.pop('success', None)
        self.failure = kwargs.pop('failure', None)
        super(ClientButton, self).__init__(*args, **kwargs)


class ClientButtonAction(ButtonAction):
    zope.interface.implements(interfaces.IClientButtonAction)
    zope.component.adapts(IFormLayer, interfaces.IClientButton)

    _success = FieldProperty(interfaces.IClientButton['success'])
    _failure = FieldProperty(interfaces.IClientButton['failure'])

    @getproperty
    def success(self):
        if self._success is None:
            return self.field.success
        return self._success

    @getproperty
    def failure(self):
        if self._failure is None:
            return self.field.failure
        return self._failure

    @setproperty
    def success(self, value):
        self._success = value

    @setproperty
    def failure(self, value):
        self._failure = value


def buttonAndHandler(title, **kwargs):

    # Add the title to button constructor keyword arguments
    kwargs['title'] = title

    # Extract directly provided interfaces:
    provides = kwargs.pop('provides', ())

    # Create button and add it to the button manager
    button = ClientButton(**kwargs)
    zope.interface.alsoProvides(button, provides)
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    buttons = f_locals.setdefault('buttons', Buttons())
    f_locals['buttons'] += Buttons(button)

    def ajaxHandler(func):
        handler = AJAXHandler(func)
        handlers = f_locals.setdefault('ajaxRequestHandlers', AJAXHandlers())
        handlers.addHandler(button.__name__, handler)
        return handler

    return ajaxHandler

##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

import zc.ajax.application
import zope.app.form.browser.interfaces
import zope.app.form.interfaces
import zope.cachedescriptors.property
import zope.formlib.form
import zope.publisher.interfaces.browser
import zope.security.checker

class FormType(type):

    def __get__(self, inst, class_):
        if inst is None:
            return self
        return self(inst)

_FormBase = FormType('_FormBase', (object, ), {})

class Form(_FormBase):

    zope.interface.implements(
        zope.publisher.interfaces.browser.IBrowserPublisher)

    __Security_checker__ = zope.security.checker.NamesChecker((
        '__call__', 'browserDefault', 'publishTraverse'))

    def __init__(self, app, request=None):
        self.app = app
        if request is None:
            request = app.request
        self.request = request
        self.context = app.context

    @zope.cachedescriptors.property.Lazy
    def prefix(self):
        return self.base_href.replace('/', '.')

    @zope.cachedescriptors.property.Lazy
    def base_href(self):
        base_href = getattr(self.app, 'base_href', None)
        if base_href is not None:
            base_href += '/'
        else:
            base_href = ''
        return base_href+self.__class__.__name__

    def get_definition(self):
        widgets = zope.formlib.form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=True)

        for widget in widgets:
            # Make sure that we have the right type of widget.
            assert hasattr(widget, 'js_config'), (
                    'Could not find an Ext widget for %r' % widget.name)

        return dict(
            widgets=[widget.js_config() for widget in widgets],
            widget_names = dict((widget.name, i)
                                for (i, widget) in enumerate(widgets)),
            actions=[dict(label=action.label,
                          url="%s/%s" % (self.base_href,
                                         action.__name__.split('.')[-1]),
                          name=action.__name__)
                     for action in self.actions]
            )

    def __call__(self):
        """Return rendered js widget configs
        """
        return zc.ajax.application.result(
            dict(definition=self.get_definition()))

    def publishTraverse(self, request, name):
        result = getattr(self, name, None)
        if isinstance(result, zope.formlib.form.Action):
            return Action(self, result)

        raise zope.publisher.interfaces.NotFound(self, name, request)
    
    def browserDefault(self, request):
        return self, ()

    def getObjectData(self, ob, extra=()):
        widgets = zope.formlib.form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            ignore_request=True)

        result = {}
        for widget in widgets:
            if widget.name in extra:
                result[widget.name] = extra[widget.name]
            else:
                v = widget.formValue(widget.context.get(ob))
                if v is not None:
                    result[widget.name] = v

        return result


class Action(object):

    zope.interface.implementsOnly(
        zope.publisher.interfaces.browser.IBrowserPublisher)

    def __init__(self, form, action):
        self.form = form
        self.action = action

    def __call__(self):
        widgets = zope.formlib.form.setUpWidgets(
            self.form.form_fields,
            self.form.prefix,
            self.form.context,
            self.form.request,
            ignore_request=True)
        data = {}
        field_errors = {}

        for input, widget in widgets.__iter_input_and_widget__():
            if (input and
                zope.app.form.interfaces.IInputWidget.providedBy(widget)
                ):
                if (not widget.hasInput()) and not widget.required:
                    continue

                name = widget.name
                if name.startswith(self.form.prefix+'.'):
                    name = name[len(self.form.prefix)+1:]

                try:
                    data[name] = widget.getInputValue()
                except zope.app.form.interfaces.InputErrors, error:

                    if not isinstance(error, basestring):
                        view = zope.component.getMultiAdapter(
                            (error, self.form.request),
                            zope.app.form.browser.interfaces.
                            IWidgetInputErrorView,
                            )
                        error = view.snippet()

                    field_errors[widget.name] = error

        if field_errors:
            return zc.ajax.application.result(dict(errors=field_errors))

        # XXX invariants and action conditions
        # XXX action validator and failure handlers

        return zc.ajax.application.result(self.action.success(data))

    def browserDefault(self, request):
        return self, ()

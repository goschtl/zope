# -*- coding: utf-8 -*-
import martian
import z3c.form
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import grokcore.security
from grokcore.view.meta.views import ViewGrokker, default_view_name

from megrok.z3cform.base.components import GrokForm

from five.grok.meta import ViewSecurityGrokker
from five.megrok.z3cform.components import FormView


def wrap_form_in_view(formClass, view_class=FormView, **kwargs):
    assert z3c.form.interfaces.IForm.implementedBy(formClass)
    # generated class must have the same name as the form
    # to allow template grokking
    viewClass = type(formClass.__name__, (view_class,), kwargs)
    viewClass.formClass = formClass
    viewClass.module_info = formClass.module_info
    return viewClass


class FiveGrokFormGrokker(ViewSecurityGrokker, ViewGrokker):
    martian.component(GrokForm)
    martian.priority(200)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.security.require, name='permission')

    def execute(self, form, config, context, layer, name, permission, **kw):
        # needed by megrok.z3cform.base
        form.__view_name__ = name
        wrappedForm = wrap_form_in_view(form)
        ViewSecurityGrokker.execute(self, wrappedForm, config, permission, **kw)
        ViewGrokker.execute(self, wrappedForm, config, context, layer, name, **kw)
        return True

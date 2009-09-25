# -*- coding: utf-8 -*-
from five.grok.meta import ViewSecurityGrokker
from megrok.z3cform.base.components import GrokForm
import martian
import grokcore.security
from plone.z3cform.layout import wrap_form, FormWrapper
from grokcore.view.meta.views import ViewGrokker, default_view_name
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from five.megrok.z3cform.directive import wrapper


class FiveGrokFormGrokker(ViewSecurityGrokker, ViewGrokker):
    martian.component(GrokForm)
    martian.priority(200)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.security.require, name='permission')
    martian.directive(wrapper, default=FormWrapper, name='formwrapper')

    def execute(self, factory, config, context, layer, name, permission,
                formwrapper, **kw):
        if getattr(factory, 'wrap', False):
            factory.__view_name__ = name
            newfactory = wrap_form(factory, formwrapper)
            newfactory.module_info = factory.module_info
            factory = newfactory
            factory.render = factory.__call__

        ViewSecurityGrokker.execute(self, factory, config, permission, **kw)
        ViewGrokker.execute(self, factory, config, context, layer, name, **kw)
        return True

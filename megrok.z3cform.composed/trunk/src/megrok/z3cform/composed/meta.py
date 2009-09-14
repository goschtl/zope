# -*- coding: utf-8 -*-

import martian
import zope.component
import grokcore.viewlet
import grokcore.component
from z3c.form.interfaces import ISubForm
from megrok.z3cform.composed import SubForm
from grokcore.view.meta.views import default_view_name
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class SubFormGrokker(martian.ClassGrokker):
    martian.component(SubForm)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.viewlet.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.viewlet.view)
    martian.directive(grokcore.viewlet.name, get_default=default_view_name)

    def grok(self, name, factory, module_info, **kw):
        factory.module_info = module_info
        return super(SubFormGrokker, self).grok(
            name, factory, module_info, **kw
            )

    def execute(self, factory, config, context, layer, view, name, **kw):
        if not factory.prefix:
            factory.prefix = name
        adapts = (context, layer, view)
        config.action(
            discriminator=('adapter', adapts, ISubForm, name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, ISubForm, name),
            )
        return True

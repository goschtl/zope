# -*- coding: utf-8 -*-

import grok
import martian

from zope import interface, component
from grok.util import make_checker
from zope.publisher.browser import BrowserPage
from grokcore.security.util import protect_getattr
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from megrok.attributetraverser.components import ViewExtension


class AttributeTraversableGrokker(martian.MethodGrokker):
    """"""
    martian.component(grok.View)

    def execute(self, factory, method, config, **kw):
        methods = grok.traversable.bind().get(factory)
        if methods:
            name = method.__name__
            if name in methods.keys():
                permission = "zope.Public"
                method_view = type(
                    factory.__name__, (factory, BrowserPage),
                    {'__call__': method})
                context = grok.context.bind().get(factory)

                adapts = (factory, IDefaultBrowserLayer)
                config.action(
                    discriminator=('adapter', adapts, interface.Interface, name),
                    callable=component.provideAdapter,
                    args=(method_view, adapts, interface.Interface, name))
                for method_name in IBrowserPage:
                    config.action(
                        discriminator=('protectName', method_view, method_name),
                        callable=protect_getattr,
                        args=(method_view, method_name, permission),
                        )
        return True


class ViewOnViewGrokker(martian.MethodGrokker):
    """
    """
    martian.component(ViewExtension)
    martian.directive(grok.view)
    martian.directive(grok.require, name='permission')

    def execute(self, factory, method, config, view, permission, **kw):
        name = method.__name__
        method_view = type(
            factory.__name__, (factory, BrowserPage),
            {'__view_name__': name})
        adapts = (view, IDefaultBrowserLayer)
        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(method_view, adapts, interface.Interface, name))
        for method_name in IBrowserPage:
            config.action(
                discriminator=('protectName', method_view, method_name),
                callable=protect_getattr,
                args=(method_view, method_name, permission))
        return True

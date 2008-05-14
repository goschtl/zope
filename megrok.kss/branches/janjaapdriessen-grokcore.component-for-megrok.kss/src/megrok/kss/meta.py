import martian

import grok
from grok.util import make_checker

from zope import component
from zope import interface
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from megrok.kss.components import KSS

class KSSGrokker(martian.ClassGrokker):
    component_class = KSS
    directives = [
        grok.view.bind(),
        grok.require.bind(name='class_permission'),
        ]

    def execute(self, factory, config, view, class_permission, **kw):
        methods = martian.util.methods_from_class(factory)

        for method in methods:
            name = method.__name__
            if name.startswith('__'):
                continue

            # Create a new class with a __view_name__ attribute so the
            # KSSServerAction class knows what method to call.

            # TODO: We should allow name directives on methods
            #view_name = grok.name.bind(default=name).get(method)

            method_view = type(
                factory.__name__, (factory, BrowserPage),
                {'__view_name__': name}
                )

            adapts = (view, IDefaultBrowserLayer)
            config.action(
                discriminator=('adapter', adapts, interface.Interface, name),
                callable=component.provideAdapter,
                args=(method_view, adapts, interface.Interface, name)
                )

            # Protect method_view with either the permission that was
            # set on the method, the default permission from the class
            # level or zope.Public.
            permission = grok.require.bind().get(method)
            if permission is None:
                permission = class_permission

            config.action(
                discriminator=('protectName', method_view, '__call__'),
                callable=make_checker,
                args=(factory, method_view, permission)
                )

        return True

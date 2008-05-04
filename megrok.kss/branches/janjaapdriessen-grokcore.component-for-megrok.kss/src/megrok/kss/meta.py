from zope import component
from zope import interface
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import martian
from martian import util

from grok.util import get_default_permission, make_checker
from grok.util import determine_class_directive

from components import KSS


class KSSGrokker(martian.ClassGrokker):
    component_class = KSS

    def grok(self, name, factory, module_info, config, **kw):
        view_context = determine_class_directive('grok.view', factory,
                                                 module_info)
        methods = util.methods_from_class(factory)
        default_permission = get_default_permission(factory)

        for method in methods:
            name = method.__name__
            if name.startswith('__'):
                continue

            # Create a new class with a __view_name__ attribute so the
            # KSSServerAction class knows what method to call.

            #We should allow name directives on methods
            #view_name = util.class_annotation(factory, 'grok.name',
            #                                  factory_name)

            method_view = type(factory.__name__, (factory, BrowserPage),
                {'__view_name__': name})

            adapts = (view_context, IDefaultBrowserLayer)
            config.action(discriminator=('adapter', adapts,
                              interface.Interface, name),
                callable=component.provideAdapter,
                args=(method_view, adapts, interface.Interface, name))

            # Protect method_view with either the permission that was
            # set on the method, the default permission from the class
            # level or zope.Public.
            permission = getattr(method, '__grok_require__',
                                 default_permission)

            config.action(discriminator=('protectName', method_view,
                               '__call__'),
                callable=make_checker,
                args=(factory, method_view, permission))

        return True

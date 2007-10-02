from zope import component
from zope import interface

from zope.publisher.browser import BrowserPage
from zope.publisher.publish import mapply
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import martian
from martian import util
from grok.util import get_default_permission, make_checker

from kss.core import KSSView

class KSSActions(KSSView):
   
    def __call__(self):
        view_name = self.__view_name__
        method = getattr(self, view_name)
        method_result = mapply(method, (), self.request)
        return self.render()

class KSSActionsGrokker(martian.ClassGrokker):
    component_class = KSSActions

    def grok(self, name, factory, context, module_info, templates):
        view_context = util.determine_class_context(factory, context)
        methods = util.methods_from_class(factory)

        # XXX We should really not make __FOO__ methods available to
        # the outside -- need to discuss how to restrict such things.
        # this is a trial ;-)
        methods = [method for method in methods if not method.__name__.startswith('_')]

        default_permission = get_default_permission(factory)

        for method in methods:
            # Create a new class with a __view_name__ attribute so the
            # KSSServerAction class knows what method to call.
        
            #We should allow name directives on methods
            #view_name = util.class_annotation(factory, 'grok.name',
            #                                  factory_name)
            method_view = type(
                factory.__name__, (factory, BrowserPage),
                {'__view_name__': method.__name__}
                )
            #if method.__name__ == 'welcome':
            #    import pdb; pdb.set_trace() 
            component.provideAdapter(
                factory = method_view, 
                adapts = (view_context, IDefaultBrowserLayer),
                provides = interface.Interface,
                name=method.__name__)

            # Protect method_view with either the permission that was
            # set on the method, the default permission from the class
            # level or zope.Public.

            permission = getattr(method, '__grok_require__',
                                 default_permission)
            make_checker(factory, method_view, permission)
        return True

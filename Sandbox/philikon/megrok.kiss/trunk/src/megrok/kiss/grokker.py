from zope import component, interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.checker import NamesChecker, defineChecker

import martian
from martian import util
from martian.error import GrokError

from megrok.kiss.component import AjaxAction

class KSSActionGrokker(martian.ClassGrokker):
    component_class = AjaxAction

    def grok(self, name, factory, context, module_info, templates):
        factory_name = factory.__name__.lower()
        view_context = util.determine_class_context(factory, context)
        view_name = util.class_annotation(factory, 'grok.name', factory_name)

        component.provideAdapter(factory,
                                 adapts=(view_context, IDefaultBrowserLayer),
                                 provides=interface.Interface,
                                 name=view_name)


        # XXX code duplication from grok.meta.ViewGrokker happening here!!!

        # protect view, public by default
        permissions = util.class_annotation(factory, 'grok.require', [])
        if not permissions:
            checker = NamesChecker(['__call__'])
        elif len(permissions) > 1:
            raise GrokError('grok.require was called multiple times in view '
                            '%r. It may only be called once.' % factory,
                            factory)
        elif permissions[0] == 'zope.Public':
            checker = NamesChecker(['__call__'])
        else:
            perm = permissions[0]
            if component.queryUtility(IPermission, name=perm) is None:
                raise GrokError('Undefined permission %r in view %r. Use '
                                'grok.define_permission first.'
                                % (perm, factory), factory)
            checker = NamesChecker(['__call__'], permissions[0])

        defineChecker(factory, checker)

        # safety belt: make sure that the programmer didn't use
        # @grok.require on any of the view's methods.
        methods = util.methods_from_class(factory)
        for method in methods:
            if getattr(method, '__grok_require__', None) is not None:
                raise GrokError('The @grok.require decorator is used for '
                                'method %r in view %r. It may only be used '
                                'for XML-RPC methods.'
                                % (method.__name__, factory), factory)
        return True


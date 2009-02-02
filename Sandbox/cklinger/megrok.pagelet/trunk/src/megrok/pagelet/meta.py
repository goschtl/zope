import grok
import martian
import zope.component
import zope.interface

import grokcore.view
import megrok.pagelet
import grokcore.component
import zope.component.zcml

from martian import util
from zope import component
from zope import interface
from martian.error import GrokError

from z3c.template.zcml import layoutTemplateDirective
from z3c.template.interfaces import ILayoutTemplate
from z3c.template.template import TemplateFactory
from zope.publisher.interfaces.browser import IBrowserPage
from grokcore.security.util import protect_getattr

from zope.publisher.interfaces.browser import IDefaultBrowserLayer


def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()


class PageletGrokker(martian.ClassGrokker):
    martian.component(megrok.pagelet.Pagelet)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_view_name)

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(PageletGrokker, self).grok(name, factory, module_info, **kw)

    def execute(self, factory, config, context, layer, name, **kw):
        # find templates
        templates = factory.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, factory.module_info, factory)
                )

        # safety belt: make sure that the programmer didn't use
        # @grok.require on any of the view's methods.
        methods = util.methods_from_class(factory)
        for method in methods:
            if grokcore.security.require.bind().get(method) is not None:
                raise GrokError('The @grok.require decorator is used for '
                                'method %r in view %r. It may only be used '
                                'for XML-RPC methods.'
                                % (method.__name__, factory), factory)

        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = name
        adapts = (context, layer)

        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(factory, adapts, interface.Interface, name),
            )
        return True

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            render = getattr(factory, 'render', None)
            base_method = getattr(render, 'base_method', False)
            return render and not base_method

        def has_no_render(factory):
            return not getattr(factory, 'render', None)
        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)



class PageletSecurityGrokker(martian.ClassGrokker):
    martian.component(megrok.pagelet.Pagelet)
    martian.directive(grokcore.security.require, name='permission')

    def execute(self, factory, config, permission, **kw):
        for method_name in IBrowserPage:
            config.action(
                discriminator=('protectName', factory, method_name),
                callable=protect_getattr,
                args=(factory, method_name, permission),
                )
        return True


class LayoutViewGrokker(martian.ClassGrokker):
    """Code resuse for View, ContentProvider and Viewlet grokkers"""
    martian.component(megrok.pagelet.LayoutView) 
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(megrok.pagelet.layout)
    martian.directive(megrok.pagelet.template)

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(LayoutViewGrokker, self).grok(name, factory, module_info, **kw)

    def execute(self, factory, config, context, layer, name, layout, template, **kw):
        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = name
        adapts = (context, layer)
	#from grokcore.component.directive import name
        # Let´s register it only for the given grok.name
	name = grokcore.component.directive.name.bind().get(self)
	path = '/'.join(factory.module_info.path.split('/')[:-1])
	template = "%s/%s" %(path, template)
        layoutfactory = TemplateFactory(template, 'text/html')
        config.action(
            discriminator = ('layoutTemplate', context, layer, name),
            callable = component.provideAdapter,
            args = (layoutfactory, adapts, ILayoutTemplate, name)
            )
        return True


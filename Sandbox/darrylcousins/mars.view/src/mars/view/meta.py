import zope.component
import zope.interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import martian
from martian.error import GrokError
from martian import util

import grok
from grok.util import (get_default_permission,
                       determine_class_directive,
                       make_checker)

import mars.view

class ViewGrokkerBase(martian.ClassGrokker):
    """Code resuse for View, ContentProvider and Viewlet grokkers"""
    component_class = None
    factory_name = ''
    view_name = ''
    layer_name = ''
    view_context = None
    provides = zope.interface.Interface

    def grok(self, name, factory, module_info, config, *kws):

        factory.module_info = module_info
        self.factory_name = factory.__name__.lower()

        self.view_layer = determine_class_directive('grok.layer',
                                               factory, module_info,
                                               default=IDefaultBrowserLayer)
        self.view_name = util.class_annotation(factory, 'grok.name',
                                          self.factory_name)
        self.view_context = determine_class_directive('grok.context',
                                               factory, module_info,
                                               default=zope.interface.Interface)

        # is name defined for template?
        # if defined a named template is looked up
        factory._template_name = util.class_annotation(factory, 'grok.template', '')

        # __view_name__ is needed to support IAbsoluteURL on views
        # TODO check how this is working for these views
        factory.__view_name__ = self.view_name

        # don't know if this would ever need to be set
        self.provides = util.class_annotation(factory, 'grok.provides',
                                                self.provides)
        # safety belt: make sure that the programmer didn't use
        # @grok.require on any of the view's methods.
        methods = util.methods_from_class(factory)
        for method in methods:
            if getattr(method, '__grok_require__', None) is not None:
                raise GrokError('The @grok.require decorator is used for '
                                'method %r in view %r. It may only be used '
                                'for XML-RPC methods.'
                                % (method.__name__, factory), factory)

        # sub classes must provide the registration
        self.register(factory, config)

        if self.view_name == 'drawing':
            print '\n'.join([str(factory), str(self.view_context), 
                 str(self.view_layer), str(self.view_name), str(self.provides)])

        permission = get_default_permission(factory)
        config.action(
            discriminator=('protectName', factory, '__call__'),
            callable=make_checker,
            args=(factory, factory, permission),
            )

        return True

    def register(self, factory, module_info):
        """Must be defined in subclasses, module_info may be necessary for
        further lookups"""
        pass


class TemplateViewGrokker(ViewGrokkerBase):
    component_class = mars.view.TemplateView

    def register(self, factory, config):

        adapts = (self.view_context, self.view_layer)
        config.action( 
            discriminator=('adapter', adapts, self.provides, self.view_name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, self.provides, self.view_name),
            )


class LayoutViewGrokker(ViewGrokkerBase):
    component_class = mars.view.LayoutView

    def register(self, factory, config):

        # is name defined for layout?
        # if defined a named template is looked up
        factory._layout_name = util.class_annotation(factory, 'mars.view.layout', '')

        adapts = (self.view_context, self.view_layer)
        config.action( 
            discriminator=('adapter', adapts, self.provides, self.view_name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, self.provides, self.view_name),
            )

class PageletViewGrokker(ViewGrokkerBase):
    component_class = mars.view.PageletView

    def register(self, factory, config):

        # is name defined for layout?
        # if defined a named template is looked up
        factory._layout_name = util.class_annotation(factory, 'mars.view.layout', '')

        adapts = (self.view_context, self.view_layer)
        config.action( 
            discriminator=('adapter', adapts, self.provides, self.view_name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, self.provides, self.view_name),
            )


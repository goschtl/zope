import martian.util
from martian.error import GrokError
from zope import interface, component
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from five import grok

from Products.Five.security import protectClass
from Globals import InitializeClass as initializeClass


def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()

class ViewGrokker(martian.ClassGrokker):
    component_class = grok.View
    directives = [
        grok.context.bind(),
        grok.layer.bind(default=IDefaultBrowserLayer),
        grok.name.bind(get_default=default_view_name),
        grok.require.bind(name='permission'),
        ]

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(ViewGrokker, self).grok(name, factory, module_info, **kw)

    def execute(self, factory, config, context, layer, name, permission, **kw):
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
        methods = martian.util.methods_from_class(factory)
        for method in methods:
            if grok.require.bind().get(method) is not None:
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

        config.action(
            discriminator = ('five:protectClass', factory),
            callable = protectClass,
            args = (factory, permission)
            )

        # Protect the class
        config.action(
            discriminator = ('five:initialize:class', factory),
            callable = initializeClass,
            args = (factory,)
            )

        return True

    def checkTemplates(self, templates, module_info, factory):
        def has_render(factory):
            return (getattr(factory, 'render', None) and
                    not util.check_subclass(factory, grok.components.GrokForm))
        def has_no_render(factory):
            return not getattr(factory, 'render', None)
        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)

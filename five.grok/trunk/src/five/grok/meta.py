import martian
from martian import util
from martian.error import GrokError
from zope import interface, component
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from five import grok

from Products.Five.security import protectClass
from Globals import InitializeClass as initializeClass

import templatereg

def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()

class ViewGrokker(martian.ClassGrokker):
    martian.component(grok.View)
    martian.directive(grok.context)
    martian.directive(grok.layer, default=IDefaultBrowserLayer)
    martian.directive(grok.name, get_default=default_view_name)
    martian.directive(grok.require, name='permission')

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(ViewGrokker, self).grok(name, factory, module_info, **kw)

    def execute(self, factory, config, context, layer, name, permission, **kw):
        if permission is None:
            permission = 'zope.Public'
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
            # XXX We haven't implemented GrokForm yet
            return (getattr(factory, 'render', None))
                    #and
                    #not util.check_subclass(factory, grok.components.GrokForm))
        def has_no_render(factory):
            return not getattr(factory, 'render', None)
        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)
        
        
class FilesystemPageTemplateGrokker(martian.GlobalGrokker):
    # do this early on, but after ModulePageTemplateGrokker, as
    # findFilesystem depends on module-level templates to be
    # already grokked for error reporting
    martian.priority(999)

    def grok(self, name, module, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False
        config.action(
            discriminator=None,
            callable=templates.findFilesystem,
            args=(module_info,)
            )
        return True

class TemplateGrokker(martian.GlobalGrokker):
    # this needs to happen before any other grokkers execute that use
    # the template registry
    martian.priority(1001)

    def grok(self, name, module, module_info, config, **kw):
        module.__grok_templates__ = templatereg.TemplateRegistry()
        return True

class ModulePageTemplateGrokker(martian.InstanceGrokker):
    martian.component(grok.components.BaseTemplate)
    # this needs to happen before any other grokkers execute that actually
    # use the templates
    martian.priority(1000)
    
    def grok(self, name, instance, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False
        config.action(
            discriminator=None,
            callable=templates.register,
            args=(name, instance)
            )
        config.action(
            discriminator=None,
            callable=instance._annotateGrokInfo,
            args=(name, module_info.dotted_name)
            )
        return True
    
class UnassociatedTemplatesGrokker(martian.GlobalGrokker):
    martian.priority(-1001)

    def grok(self, name, module, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False

        config.action(
            discriminator=None,
            callable=templates.checkUnassociated,
            args=(module_info,)
            )
        return True

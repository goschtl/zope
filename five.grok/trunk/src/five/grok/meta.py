import martian
from martian import util
from zope import interface, component
from five import grok
from five.grok.util import get_default_permission, make_checker
from grokcore.component.meta import get_context, get_name_classname
from grokcore.component.util import determine_class_directive

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
                                               #IBrowserRequest,
                                               #IBrowserPublisher,
                                               #IBrowserSkinType)

class ViewGrokker(martian.ClassGrokker):
    component_class = grok.View

    def grok(self, name, factory, module_info, config, **kw):
        view_context = get_context(module_info, factory)

        factory.module_info = module_info

        #if util.check_subclass(factory, components.GrokForm):
            ## setup form_fields from context class if we've encountered a form
            #if getattr(factory, 'form_fields', None) is None:
                #factory.form_fields = formlib.get_auto_fields(view_context)

            #if not getattr(factory.render, 'base_method', False):
                #raise GrokError(
                    #"It is not allowed to specify a custom 'render' "
                    #"method for form %r. Forms either use the default "
                    #"template or a custom-supplied one." % factory,
                    #factory)

        # find templates
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, module_info, factory)
            )

        # safety belt: make sure that the programmer didn't use
        # @grok.require on any of the view's methods.
        methods = util.methods_from_class(factory)
        for method in methods:
            if getattr(method, '__grok_require__', None) is not None:
                raise GrokError('The @grok.require decorator is used for '
                                'method %r in view %r. It may only be used '
                                'for XML-RPC methods.'
                                % (method.__name__, factory), factory)

        # grab layer from class or module
        view_layer = determine_class_directive('grok.layer',
                                               factory, module_info,
                                               default=IDefaultBrowserLayer)

        view_name = get_name_classname(factory)
        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = view_name
        adapts = (view_context, view_layer)

        config.action(
            discriminator=('adapter', adapts, interface.Interface, view_name),
            callable=component.provideAdapter,
            args=(factory, adapts, interface.Interface, view_name),
            )

        permission = get_default_permission(factory)
        config.action(
            discriminator=('protectName', factory, '__call__'),
            callable=make_checker,
            args=(factory, factory, permission),
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

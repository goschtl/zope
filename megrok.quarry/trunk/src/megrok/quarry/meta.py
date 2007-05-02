import grok
from megrok import quarry
from grok import util, components, formlib
from grok.error import GrokError

from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.viewlet.interfaces import IViewletManager, IViewlet
from zope.security.permission import Permission
from zope.security.interfaces import IPermission
from zope.security.checker import NamesChecker, defineChecker

from zope.dottedname.resolve import resolve
from zope import interface, component
import zope.component.interface

class LayerGrokker(grok.ClassGrokker):
    component_class = quarry.Layer


class SkinGrokker(grok.ClassGrokker):
    component_class = quarry.Skin

    def register(self, context, name, factory, module_info, templates):
        layer = util.class_annotation(factory, 'quarry.layer',
                                    None) or module_info.getAnnotation('grok.layer',
                                    None) or grok.IDefaultBrowserLayer
        name = util.class_annotation(factory, 'grok.name', factory.__name__.lower())
        zope.component.interface.provideInterface(name, layer, IBrowserSkinType)


class ViewGrokker(grok.ClassGrokker):
    component_class = quarry.View

    def register(self, context, name, factory, module_info, templates):
        view_context = util.determine_class_context(factory, context)

        factory.module_info = module_info
        factory_name = factory.__name__.lower()

        if util.check_subclass(factory, components.GrokForm):
            # setup form_fields from context class if we've encountered a form
            if getattr(factory, 'form_fields', None) is None:
                factory.form_fields = formlib.get_auto_fields(view_context)

            if not getattr(factory.render, 'base_method', False):
                raise GrokError(
                    "It is not allowed to specify a custom 'render' "
                    "method for form %r. Forms either use the default "
                    "template or a custom-supplied one." % factory,
                    factory)

        # find templates
        if util.class_annotation(factory, 'grok.template',
                                 None):
            raise GrokError(
                "%s may not use grok.template, use quarry.template instead."
                % factory.__name__, factory)

        template_name = util.class_annotation(factory, 'quarry.template',
                                              None)
        if template_name is None:
            template_name = factory_name
            
        template = templates.get(template_name)

            
        if factory_name != template_name:
            # grok.template is being used
            if templates.get(factory_name):
                raise GrokError("Multiple possible templates for view %r. It "
                                "uses grok.template('%s'), but there is also "
                                "a template called '%s'."
                                % (factory, template_name, factory_name),
                                factory)
            # no conflicts, lets try and load the template
            # using grok.Template('with.dotted.name')
            try:
                factory.template = resolve(template_name)
                # accept string and unicode objects, useful if .__doc__ is referenced
                if isinstance(factory.template, (str, unicode)):
                    factory.template = grok.PageTemplate(factory.template)
            except ImportError:
                # verify this is a dotted name
                if template_name.find('.') >=0:
                    raise GrokError(
                        "'%s' is not importable. Check the path and"
                        "be sure it's a grok.PageTemplate,"
                        "grok.PageTemplateFile, string, or unicode object"
                        % template_name, factory)

        # support in-class imports template = grok.PageTemplateFile
        factory_template =  getattr(factory, 'template', None)

        if template:
            if (getattr(factory, 'render', None) and not
                util.check_subclass(factory, components.GrokForm)):
                # we do not accept render and template both for a view
                # (unless it's a form, they happen to have render.
                raise GrokError(
                    "Multiple possible ways to render view %r. "
                    "It has both a 'render' method as well as "
                    "an associated template." % factory, factory)

            templates.markAssociated(template_name)
            factory.template = template
        elif factory_template:
            pass
        else:
            if not getattr(factory, 'render', None):
                # we do not accept a view without any way to render it
                raise GrokError("View %r has no associated template or "
                                "'render' method." % factory, factory)

        view_layer = util.class_annotation(factory, 'grok.layer',
                                           None) or module_info.getAnnotation('grok.layer',
                                               None) or IDefaultBrowserLayer

        view_name = util.class_annotation(factory, 'grok.name',
                                          factory_name)
        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = view_name
        component.provideAdapter(factory,
                                 adapts=(view_context, view_layer),
                                 provides=interface.Interface,
                                 name=view_name)

        # protect view, public by default
        default_permission = util.get_default_permission(factory)
        util.make_checker(factory, factory, default_permission)
    
        # safety belt: make sure that the programmer didn't use
        # @grok.require on any of the view's methods.
        methods = util.methods_from_class(factory)
        for method in methods:
            if getattr(method, '__grok_require__', None) is not None:
                raise GrokError('The @grok.require decorator is used for '
                                'method %r in view %r. It may only be used '
                                'for XML-RPC methods.'
                                % (method.__name__, factory), factory)




# class ViewletManagerGrokker(grok.ClassGrokker):
#     component_class = (grok.ViewletManager, grok.OrderedViewletManager)

#     def register(self, context, name, factory, module_info, templates):

#         factory.module_info = module_info # to make /static available

#         name = grok.util.class_annotation(factory, 'grok.name', factory.__name__.lower())
#         view_layer = util.class_annotation(factory, 'grok.layer',
#                                                     None) or module_info.getAnnotation('grok.layer',
#                                                      None) or IDefaultBrowserLayer
        
#         view_context = util.determine_class_context(factory, context)
#         component.provideAdapter(factory,
#                                  adapts=(None, # TODO: Make configurable
#                                          view_layer, # TODO: Make configurable
#                                          view_context),
#                                  provides=IViewletManager,
#                                  name=name)

            
# class ViewletGrokker(grok.ClassGrokker):
#     component_class = grok.Viewlet
                
#     def register(self, context, name, factory, module_info, templates):
#         # Try to set up permissions (copied from the View grokker)

#         factory.module_info = module_info # to make /static available
#         factory_name = factory.__name__.lower()
        
#         permissions = grok.util.class_annotation(factory, 'grok.require', [])
#         if not permissions:
#             checker = NamesChecker(['update', 'render'])
#         elif len(permissions) > 1:
#             raise GrokError('grok.require was called multiple times in viewlet '
#                             '%r. It may only be called once.' % factory,
#                             factory)
#         elif permissions[0] == 'zope.Public':
#             checker = NamesChecker(['update','render'])
#         else:
#             perm = permissions[0]
#             if component.queryUtility(IPermission, name=perm) is None:
#                 raise GrokError('Undefined permission %r in view %r. Use '
#                             'grok.define_permission first.'
#                             % (perm, factory), factory)
#             checker = NamesChecker(['update','render'], permissions[0])
        
#         defineChecker(factory, checker)


#         # find templates
#         template_name = util.class_annotation(factory, 'grok.template',
#                                               factory_name)
#         template = templates.get(template_name)

#         if factory_name != template_name:
#             # grok.template is being used
#             if templates.get(factory_name):
#                 raise GrokError("Multiple possible templates for view %r. It "
#                                 "uses grok.template('%s'), but there is also "
#                                 "a template called '%s'."
#                                 % (factory, template_name, factory_name),
#                                 factory)

#         factory_template = getattr(factory,'template', None)
        
#         if template:
#             if (getattr(factory, 'render', None) and not
#                 util.check_subclass(factory, components.GrokForm) and not
#                 util.check_subclass(factory, components.Viewlet)):
#                 # we do not accept render and template both for a view
#                 # (unless it's a form, they happen to have render.)
#                 # Forms currently not implemented in viewlets.
#                 raise GrokError(
#                     "Multiple possible ways to render view %r. "
#                     "It has both a 'render' method as well as "
#                     "an associated template." % factory, factory)

#             templates.markAssociated(template_name)
#             factory.template = template
#         elif factory_template and isinstance(factory_template, (components.PageTemplate, components.PageTemplateFile)):
#             pass
#         else:
#             if not getattr(factory, 'render', None):
#                 # we do not accept a view without any way to render it
#                 raise GrokError("View %r has no associated template or "
#                                 "'render' method." % factory, factory)

        
#         # New directive
#         viewletmanager = grok.util.class_annotation(factory, 'grok.viewletmanager', [])
#         layer = util.class_annotation(factory, 'grok.layer',
#                                             None) or module_info.getAnnotation('grok.layer',
#                                              None) or IDefaultBrowserLayer
       
#         component.provideAdapter(factory,
#                                  adapts=(None, # TODO: Make configurable
#                                          layer,
#                                          IBrowserView,
#                                          viewletmanager),
#                                  provides=IViewlet,
#                                  name=name)


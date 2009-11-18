import martian
import grokcore.view
import grokcore.component
import grokcore.viewlet

from z3c.form import field
from martian.error import GrokError
from zope.interface import Interface
from megrok.z3cform.base import directives
from megrok.z3cform.base import components
from zope.interface.interfaces import IInterface
from grokcore.view.meta.views import ViewGrokker, default_view_name
from z3c.form.zcml import widgetTemplateDirective
from grokcore.formlib.formlib import most_specialized_interfaces
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


def get_auto_fields(context):
    """Get the form fields for context.
    This methods is the same than for formlib implementation, but use
    z3cform fields instead.
    """
    # for an interface context, we generate them from that interface
    if IInterface.providedBy(context):
        return field.Fields(context)
    # if we have a non-interface context, we're autogenerating them
    # from any schemas defined by the context
    fields = field.Fields(*most_specialized_interfaces(context))
    # we pull in this field by default, but we don't want it in our form
    fields = fields.omit('__name__')
    return fields


class FormGrokker(martian.ClassGrokker):

    martian.component(components.GrokForm)
    martian.directive(grokcore.component.context)
    # execute this grokker before grokcore.view's ViewGrokker
    martian.priority(martian.priority.bind().get(ViewGrokker) + 10)

    def execute(self, form, context, **kw):

        # Set fields by default.
        if isinstance(form.fields, components.DefaultFields):
            form.fields = get_auto_fields(context)


        return True


class WidgetTemplateGrokker(martian.ClassGrokker):
    """ grokker for widget templates """
    martian.component(components.WidgetTemplate)
    martian.directive(grokcore.component.context, default=Interface)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.view.template)
    martian.directive(grokcore.viewlet.view)
    martian.directive(directives.field)
    martian.directive(directives.mode)
    martian.directive(directives.widget)

    def grok(self, name, factory, module_info, **kw):
        factory.module_info = module_info
        return super(WidgetTemplateGrokker, self).grok(
                          name, factory, module_info, **kw)

    def execute(self, factory, config, context, layer,
                template, view, field, widget, mode, **kw):
        template_path = '/'.join(factory.module_info.path.split('/')[:-1])
        template = "%s/%s" %(template_path, template)
        widgetTemplateDirective(config, template, context, layer,
                    view=view, field=field, widget=widget, mode=mode)
        return True

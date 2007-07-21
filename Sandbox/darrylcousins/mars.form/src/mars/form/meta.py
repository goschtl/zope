import os

import zope.component
import zope.interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.pagetemplate.interfaces import IPageTemplate

from z3c.form.interfaces import INPUT_MODE
from z3c.form.widget import WidgetTemplateFactory
from z3c.template.template import TemplateFactory
from z3c.template.interfaces import ILayoutTemplate

import martian
from martian import util
from martian.error import GrokError

import grok
from grok.util import check_adapts

import mars.form
import mars.template
from mars.view.meta import ViewGrokkerBase


class FormViewGrokker(ViewGrokkerBase):
    component_class = mars.form.FormView

    def register(self, factory, module_info):

        # is name defined for layout?
        # if defined a named template is looked up
        factory._layout_name = util.class_annotation(factory, 'mars.view.layout', '')

        zope.component.provideAdapter(factory,
                                 adapts=(self.view_context, self.view_layer),
                                 provides=self.provides,
                                 name=self.view_name)

class WidgetTemplateFactoryGrokker(martian.ClassGrokker):
    component_class = mars.form.WidgetTemplateFactory
    provides = IPageTemplate

    def grok(self, name, factory, context, module_info, templates):
        view_context = util.determine_class_context(factory, context)
        factory.module_info = module_info
        factory_name = factory.__name__.lower()

        # we need a path to the file containing the template
        template_name = util.class_annotation(factory, 'grok.template',
                                              factory_name)
        filepath = os.path.join(os.path.dirname(module_info.path), template_name)
        if not os.path.exists(filepath):
            filepath = None
            if os.path.exists(template_name):
                filepath = template_name
        if filepath is None:
            raise GrokError("No template found for %s."
                            " Please use grok.template to define path to the"
                            " file containing the template"
                            % (factory.__name__),
                            factory)

        provides = util.class_annotation(factory, 'grok.provides', self.provides)
        contentType = util.class_annotation(factory,
                                    'mars.template.content_type', 'text/html')
        view_layer = util.class_annotation(factory, 'mars.layer.layer',
                                       None) or module_info.getAnnotation('mars.layer.layer',
                                       None) or IDefaultBrowserLayer
        mode = util.class_annotation(factory, 'grok.name', INPUT_MODE)
        view = util.class_annotation(factory, 'mars.form.view', None)
        field = util.class_annotation(factory, 'mars.form.field', None)
        widget = util.class_annotation(factory, 'mars.form.widget', None)

        factory = WidgetTemplateFactory(filepath, contentType)
        zope.interface.directlyProvides(factory, provides)
        #print '\nname:', mode,'context:', view_context,'factory:',\
        #      factory, 'provides', provides, 'view:', view, 'field:', field, \
        #      'widget:', widget, '\n'
        zope.component.provideAdapter(factory,
                                 adapts=(view_context, view_layer, view, field, widget),
                                 provides=provides,
                                 name=mode)
        return True


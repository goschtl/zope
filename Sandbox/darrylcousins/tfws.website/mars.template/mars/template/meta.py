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
from grok.util import determine_class_directive

import mars.template

# TODO raise errors if anything missing?
class TemplateFactoryGrokkerBase(martian.ClassGrokker):
    component_class = None
    provides = None

    def grok(self, name, factory, module_info, config, *kws):
     
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

        macro = util.class_annotation(factory, 'mars.template.macro', None)
        contentType = util.class_annotation(factory,
                                    'mars.template.content_type', 'text/html')
        view_layer = determine_class_directive('grok.layer',
                                               factory, module_info,
                                               default=IDefaultBrowserLayer)
        view_name = util.class_annotation(factory, 'grok.name', u'')
        view_context = determine_class_directive('grok.context',
                                               factory, module_info,
                                               default=zope.interface.Interface)
        provides = util.class_annotation(factory, 'grok.provides', self.provides)

        # now make the template factory proper
        factory = TemplateFactory(filepath, contentType, macro)


        zope.interface.directlyProvides(factory, provides)

        adapts = (view_context, view_layer)

#        print '\n',view_name,'\n',factory,'\n',provides,'\n',adapts

        config.action( 
            discriminator=('adapter', adapts, provides, view_name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, provides, view_name),
            )
        return True


class TemplateFactoryGrokker(TemplateFactoryGrokkerBase):
    component_class = mars.template.TemplateFactory
    provides = IPageTemplate

class LayoutFactoryGrokker(TemplateFactoryGrokkerBase):
    component_class = mars.template.LayoutFactory
    provides = ILayoutTemplate



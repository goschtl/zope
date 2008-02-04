import os

import zope.component
import zope.interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.pagetemplate.interfaces import IPageTemplate

from z3c.macro.zcml import MacroFactory
from z3c.macro.interfaces import IMacroTemplate

import martian
from martian import util
from martian.error import GrokError

import grok
from grok.util import determine_class_directive

import mars.macro

# TODO raise errors if anything missing?
class MacroFactoryGrokker(martian.ClassGrokker):
    component_class = mars.macro.MacroFactory

    def grok(self, name, factory, module_info, config, **kws):

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
                            " Please use grok.template to define path to file."
                            " containing the template"
                            % (factory.__name__),
                            factory)

        contentType = util.class_annotation(factory,
                                               'mars.macro.content_type',
                                               'text/html')
        view_layer = determine_class_directive('grok.layer',
                                               factory, module_info,
                                               default=IDefaultBrowserLayer)
        view_name = util.class_annotation(factory, 'grok.name', factory_name)
        macro = util.class_annotation(factory, 'mars.macro.macro', view_name)
        view = util.class_annotation(factory, 'mars.macro.view', IBrowserView)
        self.view_context = determine_class_directive('grok.context',
                                               factory, module_info,
                                               default=zope.interface.Interface)

        factory = MacroFactory(filepath, macro, contentType)

        adapts = (view_context, view, view_layer)

        config.action( 
            discriminator=('adapter', adapts, IMacroTemplate, view_name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, IMacroTemplate, view_name),
            )
        return True



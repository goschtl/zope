import os
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


class LayoutViewGrokker(martian.ClassGrokker):
    """Code resuse for View, ContentProvider and Viewlet grokkers"""
    martian.component(megrok.pagelet.Layout) 
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(megrok.pagelet.template)


    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(LayoutViewGrokker, self).grok(name, factory, module_info, **kw)


    def execute(self, factory, config, context, layer, name, template, **kw):
        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = name
        adapts = (context, layer)
	#from grokcore.component.directive import name
        # Let register it only for the given grok.name
	name = grokcore.component.directive.name.bind().get(self)
	module_info = factory.module_info
	path = module_info.getResourcePath('')
	template = "%s%s" %(path, template)
        # Ok i use now the check in the zope.pagetemplatefile package.
        # I think this need some imporovement.
	try:
            layoutfactory = TemplateFactory(template, 'text/html')
	except ValueError, e:
	    raise GrokError("The Template %s is not found in module %s"
	                     %(template, module_info.getModule()), module_info.getModule())
        config.action(
            discriminator = ('layoutTemplate', context, layer, name),
            callable = component.provideAdapter,
            args = (layoutfactory, adapts, ILayoutTemplate, name)
            )
        return True

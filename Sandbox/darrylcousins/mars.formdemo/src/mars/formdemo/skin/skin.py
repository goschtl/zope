import zope.interface
from zope.viewlet.viewlet import CSSViewlet
from zope.publisher.interfaces.browser import IBrowserPage

import z3c.formui

import grok

import mars.layer
import mars.template
import mars.viewlet
import mars.resource

from mars.formdemo.layer import (IDemoBrowserLayer,
                                 IDemoDivBrowserLayer,
                                 IDemoTableBrowserLayer)

class MarsFormDemo(mars.layer.Skin):
    """The ``marsformdemo`` browser skin."""
    mars.layer.layer(IDemoDivBrowserLayer)

class MarsTableFormDemo(mars.layer.Skin):
    """The ``marstableformdemo`` browser skin."""
    mars.layer.layer(IDemoTableBrowserLayer)

mars.layer.layer(IDemoBrowserLayer)

# main template for pages (note the context!)
class Template(mars.template.LayoutFactory):
    grok.context(IBrowserPage)
    grok.template('template.pt')

# css viewletmanager
class CSS(mars.viewlet.ViewletManager):
    zope.interface.implements(z3c.formui.interfaces.ICSS)
    grok.name('ICSS')
    grok.context(zope.interface.Interface)

# javascript viewletmanager
class JavaScript(mars.viewlet.ViewletManager):
    grok.name('IJavaScript')
    grok.context(zope.interface.Interface)

# css viewlet
DemoCSSViewlet = CSSViewlet('demo.css')
class FormDemoCSSViewlet(mars.viewlet.SimpleViewlet, DemoCSSViewlet):
    grok.name('demo.css')
    grok.context(zope.interface.Interface)
    mars.viewlet.manager(CSS)


# resources (++resource++demo.css)
class DemoStyle(mars.resource.ResourceFactory):
    grok.name('demo.css')
    mars.resource.file('demo.css')

# image resource directory (++resource++images)
class Images(mars.resource.ResourceDirectoryFactory):
    mars.resource.directory('images')

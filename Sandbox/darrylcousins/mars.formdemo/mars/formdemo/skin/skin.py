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

class Template(mars.template.LayoutFactory):
    """main template for pages (note the context!)"""
    grok.context(IBrowserPage)
    grok.template('template.pt')

class CSSManager(mars.viewlet.ViewletManager):
    """css viewletmanager"""
    zope.interface.implements(z3c.formui.interfaces.ICSS)
    grok.name('ICSS')
    grok.context(zope.interface.Interface)

class JavaScriptManager(mars.viewlet.ViewletManager):
    """javascript viewletmanager"""
    grok.name('IJavaScript')
    grok.context(zope.interface.Interface)

DemoCSSViewlet = CSSViewlet('demo.css')
class FormDemoCSSViewlet(mars.viewlet.SimpleViewlet, DemoCSSViewlet):
    """css viewlet"""
    grok.name('demo.css')
    grok.context(zope.interface.Interface)
    mars.viewlet.manager(CSSManager)

class DemoStyle(mars.resource.ResourceFactory):
    """resources (++resource++demo.css)"""
    grok.name('demo.css')
    mars.resource.file('demo.css')

class Img(mars.resource.ResourceDirectoryFactory):
    """image resource directory (++resource++img)"""
    mars.resource.directory('img')

class SpreadSheetImages(mars.resource.ResourceDirectoryFactory):
    """image resource directory (++resource++SpreadsheetImages)"""
    grok.name('SpreadsheetImages')
    mars.resource.directory('images')

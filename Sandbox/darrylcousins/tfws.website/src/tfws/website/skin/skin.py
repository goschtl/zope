import zope.component
import zope.interface
from zope.viewlet.viewlet import CSSViewlet
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.browser import absoluteURL
from zope.app.component import hooks

import z3c.formui

import grok

import mars.layer
import mars.template
import mars.viewlet
import mars.resource

from tfws.website.layer import IWebsiteLayer

# module level layer definition
mars.layer.layer(IWebsiteLayer)

class TFWSWebsite(mars.layer.Skin):
    """The ``tfwswebsite`` browser skin."""
    pass

class Template(mars.template.LayoutFactory):
    """main template for pages (note the context!)"""
    grok.context(IBrowserPage)
    grok.template('template.pt')

class NavigationManager(mars.viewlet.ViewletManager):
    """navigation column viewletmanager"""
    grok.name('INavigationColumn')
    grok.context(zope.interface.Interface)

class CSSManager(mars.viewlet.ViewletManager):
    """css viewletmanager"""
    zope.interface.implements(z3c.formui.interfaces.ICSS)
    grok.name('ICSS')
    grok.context(zope.interface.Interface)

class JavaScriptManager(mars.viewlet.ViewletManager):
    """javascript viewletmanager"""
    grok.name('IJavaScript')
    grok.context(zope.interface.Interface)

WebsiteCSSViewlet = CSSViewlet('website.css')
class FormDemoCSSViewlet(mars.viewlet.SimpleViewlet, WebsiteCSSViewlet):
    """css viewlet"""
    grok.name('website.css')
    grok.context(zope.interface.Interface)
    mars.viewlet.manager(CSSManager)

class DemoStyle(mars.resource.ResourceFactory):
    """resources (++resource++website.css)"""
    grok.name('website.css')
    mars.resource.file('website.css')

class Images(mars.resource.ResourceDirectoryFactory):
    """image resource directory (++resource++images)"""
    mars.resource.directory('images')

class ISiteURL(zope.interface.Interface):
    pass

class SiteURL(grok.MultiAdapter):
    """Provides siteURL to all context"""
    grok.name('siteURL')
    grok.context(zope.interface.Interface)
    zope.interface.implements(ISiteURL)
    zope.component.adapts(zope.interface.Interface, IHTTPRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return absoluteURL(hooks.getSite(), self.request)


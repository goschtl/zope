import zope.component
import zope.interface
from zope.component.interfaces import ComponentLookupError
from zope.publisher.browser import BrowserPage
from zope.publisher.publish import mapply
from zope.pagetemplate.interfaces import IPageTemplate

from z3c.template.interfaces import ILayoutTemplate
from z3c.pagelet.interfaces import IPagelet

import grok
from grok.interfaces import IGrokView

class TemplateViewBase(object):
    """Mixin to reuse render method"""
    template = None
    _template_name = u'' # will be set if grok.template defined
    _template_interface = IPageTemplate

    def render(self):
        if self.request.response.getStatus() in (302, 303):
            return
        template = getattr(self, 'template', None)
        if template is None:
            template = zope.component.getMultiAdapter(
                (self, self.request), self._template_interface, 
                name=self._template_name)
            return template(self)
        return template(self)


class TemplateView(TemplateViewBase, BrowserPage):

    def __init__(self, context, request):
        super(TemplateView, self).__init__(context, request)


class LayoutViewBase(object):
    layout = None
    _layout_name = u'' # will be set if mars.view.layout defined
    _layout_interface = ILayoutTemplate

    def __call__(self):
        update = getattr(self, 'update', None)
        if update is not None:
            self.update()
        if self.request.response.getStatus() in (302, 303):
            return
        layout = getattr(self, 'layout', None)
        if layout is None:
            layout = zope.component.getMultiAdapter(
                    (self, self.request), self._layout_interface, 
                    name=self._layout_name)
            #print layout
            #return u'Layout'
            return layout(self)
        return layout(self)

class LayoutView(LayoutViewBase, BrowserPage):

    __init__ = BrowserPage.__init__

class PageletView(TemplateViewBase, LayoutViewBase, BrowserPage):
    zope.interface.implements(IPagelet)

    __init__ = BrowserPage.__init__

class SimpleView

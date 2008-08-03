import lxml.etree
import lxml.html

from zope import interface
from zope import component

from zope.publisher.browser import BrowserView
from zope.contentprovider.interfaces import IContentProvider

from z3c.layout import interfaces

import insertion

class LayoutView(BrowserView):
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.layout = interfaces.ILayout(context)
                
    def __call__(self):
        tree = self.layout.parse()

        # lookup content provider components
        content_providers = self._get_content_providers()
        
        # update content providers
        for region, provider in content_providers:
            provider.update()

        # render and insert content providers
        for region, provider in content_providers:
            self._insert_provider(tree, region, provider)

        return lxml.html.tostring(tree, pretty_print=True).rstrip('\n')
    
    def _insert_provider(self, tree, region, provider):
        # render and wrap provided content
        html = provider.render() 
        provided = lxml.html.fromstring(
            u"<div>%s</div>" % html)

        # look up insertion method
        try:
            insert = getattr(insertion, region.mode)
        except AttributeError:
            raise ValueError("Invalid mode: %s" % repr(region.mode))

        # insert provided content into nodes
        nodes = tree.xpath(region.xpath)
        for node in nodes:
            insert(node, provided)

    def _get_content_providers(self):
        """Lookup content providers for regions."""
        
        results = []
        
        for region in self.layout.regions:
            name = region.provider

            if name is not None:
                provider = component.queryMultiAdapter(
                    (region, self.request, self), IContentProvider, name=name)
            else:
                provider = component.queryMultiAdapter(
                    (region, self.request, self), IContentProvider)

            if provider is None:
                raise ValueError(
                    "Unable to determine content "
                    "provider for region '%s'." % region.name)

            provider.__name__ = region.name
            results.append((region, provider))

        return results            

import lxml.etree
import lxml.html

from zope import interface
from zope import component

from zope.publisher.browser import BrowserView
from zope.contentprovider.interfaces import IContentProvider

from z3c.layout import interfaces

from plone.memoize.view import memoize

import insertion

class LayoutView(BrowserView):
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        
        self._layout = interfaces.ILayout(context)
        self.mapping = self._get_region_provider_mapping()

    def __call__(self):
        # parse tree
        tree = self._layout.parse()

        # render and insert content providers
        for region, provider in self.mapping.values():
            self._insert_provider(tree, region, provider)

        return lxml.html.tostring(tree, pretty_print=True).rstrip('\n')

    def _insert_provider(self, tree, region, provider):
        # render and wrap provided content
        html = provider.render() 
        provided = lxml.html.fromstring(
            u"<div>%s</div>" % html)

        insertion.insert(tree, region, provided)

    def _get_provider(self, region):
        """Lookup content provider for region."""

        name = region.provider

        factory = interfaces.IContentProviderFactory(region, None)
        if factory is not None:
            return factory(self.context, self.request, self)

        if name is not None:
            return component.queryMultiAdapter(
                (self.context, self.request, self), IContentProvider, name=name)

        return None
    
    @memoize
    def _get_region_provider_mapping(self):
        mapping = {}

        for region in self._layout.regions:
            provider = self._get_provider(region)

            if provider is not None:
                provider.__name__ = region.name
                mapping[region.name] = (region, provider)

        # update content providers
        for region, provider in mapping.values():
            provider.update()

        return mapping

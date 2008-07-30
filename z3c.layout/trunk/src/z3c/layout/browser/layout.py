import lxml.etree
import lxml.html

from zope import interface
from zope import component

from zope.publisher.browser import BrowserView
from zope.contentprovider.interfaces import IContentProvider

from z3c.layout.interfaces import ILayout
from z3c.layout.interfaces import ILayoutAssignment
from z3c.layout.browser.interfaces import ITreeContentProvider

from urlparse import urlparse

class LayoutView(BrowserView):
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        
        self.assignment = assignment = ILayoutAssignment(context)
        self.layout = component.getUtility(
            ILayout, name=assignment.name)
        
    def __call__(self):
        tree = lxml.html.parse(self.layout.template)        
        rebase(tree, '++resource++%s' % self.layout.resource_directory)

        # lookup content provider components
        region_content_providers = self._get_region_content_providers()
        tree_content_providers = self._get_tree_content_providers()
        
        # update content providers
        for region, provider in region_content_providers:
            provider.update()

        for provider in tree_content_providers:
            provider.update()

        # render and insert region content providers
        for region, provider in region_content_providers:
            html = provider.render()
            subtree = tree.xpath(region.xpath)

            if len(subtree) != 1:
                continue

            subtree = subtree[0]

            del subtree[:]

            provided = lxml.html.fromstring(
                u"<div>%s</div>" % html)

            subtree.text = provided.text
            subtree.extend(tuple(provided))

        # render and insert tree content providers
        for provider in tree_content_providers:
            provider.insert(tree)
            
        return lxml.html.tostring(tree, pretty_print=True).rstrip('\n')

    def _get_region_content_providers(self):
        """Lookup region content providers."""
        
        results = []
        provider_map = self.assignment.provider_map
        
        for region in self.layout.regions:
            name = provider_map.get(region.name, None)
            if name is not None:
                provider = component.queryMultiAdapter(
                    (region, self.request, self), IContentProvider, name=name)
                
                if provider is not None:
                    provider.__name__ = region.name
                    results.append((region, provider))

        return results

    def _get_tree_content_providers(self):
        """Lookup tree content providers.

        To play nice with viewlet managers and content provider
        adapters alike, we first lookup factories providing the
        ``IContentProvider`` interface, then return all providers that
        implement the ``ITreeContentProvider`` interface.
        """
        
        sm = component.getSiteManager()
        required = self.context, self.request, self

        factories = sm.adapters.lookupAll(
            map(interface.providedBy, required), IContentProvider)

        return [factory(*required) for name, factory in factories if \
                ITreeContentProvider.implementedBy(factory)]
            
def rebase(tree, prefix):
    """Rebase resources.

    Parse through an lxml tree, adding the ``prefix`` to all tag
    attributes that point to URL-relative layout resources:

    Tag        Attribute
    -----------------------------
    img        src
    
    >>> from z3c.layout.browser.layout import rebase
    >>> import lxml

    >>> html = '''\
    ... <html>
    ...   <head>
    ...      <link href="some/url" />
    ...   </head>
    ...   <body>
    ...      <img src="some/url" />
    ...      <img src="http://host/some/url" />
    ...   </body>
    ... </html>'''

    >>> tree = lxml.etree.fromstring(html)
    >>> rebase(tree, '++foo++')
    >>> print lxml.etree.tostring(tree, pretty_print=True)
    <html>
      <head>
         <link href="++foo++/some/url"/>
      </head>
      <body>
         <img src="++foo++/some/url"/>
         <img src="http://host/some/url"/>
      </body>
    </html>
    
    """

    for xpath, attribute in (('.//img', 'src'),
                             ('.//head/link', 'href')):
        for element in tree.findall('%s[@%s]' % (xpath, attribute)):
            value = element.get(attribute)
            protocol, host = urlparse(value)[:2]

            # rebase if host is trivial
            if not host:
                element.set(attribute, '%s/%s' % (prefix, value))

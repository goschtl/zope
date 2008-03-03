from provider import ResourceIncludeProvider

from time import time
from plone.memoize import ram

class ResourceViewlet(ResourceIncludeProvider):
    def __init__(self, context, request, view, manager):
        ResourceIncludeProvider.__init__(self, context, request, view)

class CacheOneHourViewlet(ResourceViewlet):
    @ram.cache(lambda *args: time() // (60 * 60))
    def render(self):
        return ResourceViewlet.render(self)

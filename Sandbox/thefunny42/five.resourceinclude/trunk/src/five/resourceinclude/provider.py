
from z3c.resourceinclude import provider

class ResourceIncludeProvider(provider.ResourceIncludeProvider):

    def update(self):
        super(ResourceIncludeProvider, self).update()
        self.collector = self.collector.__of__(self.context)

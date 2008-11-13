
from z3c.resourceinclude import manager
import Acquisition

class ResourceManager(manager.ResourceManager, Acquisition.Implicit):

    def searchResource(self, request, name):
        resource = super(ResourceManager, self).searchResource(request, name)
        if resource:
            return resource.__of__(self)
        return resource


class ResourceManagerFactory(manager.ResourceManagerFactory):

    def __call__(self):
        return ResourceManager()

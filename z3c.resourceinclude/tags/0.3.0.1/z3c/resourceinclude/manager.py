from zope import interface
from zope import component

from interfaces import IResourceManager

class ResourceManager(object):
    interface.implements(IResourceManager)
    
    def __init__(self):
        self.names = []
        
    def __call__(self, request):
        return self

    def available(self):
        return True

    def add(self, name):
        if name not in self.names:
            self.names.append(name)

    def searchResource(self, request, name):
        return component.queryAdapter(
                request, name=name)

    def getResources(self, request):
        resources = []
        
        for name in self.names:
            if '/' in name:
                name, path = name.split('/', 1)
            else:
                path = None

            resource = self.searchResource(request, name)

            if path is not None:
                resource = resource[path]
                name = "/".join((name, path))

            resources.append((name, resource))

        return resources


class ResourceManagerFactory(object):

    interface.implements(component.IFactory)

    title = "z3c.resourceinclude.ResourceManager"
    descript = "Build a resource manager"

    def getInterfaces(self):
        return [IResourceManager,]

    def __call__(self):
        return ResourceManager()


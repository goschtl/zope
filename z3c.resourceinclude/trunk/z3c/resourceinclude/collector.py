from zope import interface
from zope import component

from zope.publisher.interfaces.browser import IBrowserRequest

from interfaces import IResourceCollector
from interfaces import IResourceManager

class ResourceCollector(object):
    interface.implements(IResourceCollector)
    component.adapts(IBrowserRequest)
    
    def __init__(self, request):
        self.request = request

    def collect(self):
        resources = []
        names = []
        
        for name, manager in self._get_managers():
            items = manager.getResources(self.request)

            # filter out duplicates
            rs = [resource for name, resource in items if name not in names]
            names.extend((name for name, resource in items)) 

            # sort
            self.sort(rs)

            # merge
            self.merge(rs)

            resources.extend(rs)

        return tuple(resources)

    def sort(self, resources):
        # order resources by content type
        resources.sort(key=lambda resource: resource.context.content_type)
        return resources

    def merge(self, resources):
        return resources

    def _get_managers(self):
        managers = [(name, manager) for name, manager in \
                    component.getAdapters((self.request,), IResourceManager) if \
                    manager.available()]
        
        managers.sort(key=lambda (name, manager): name)

        return managers

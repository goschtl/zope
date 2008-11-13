
from z3c.resourceinclude import collector
import Acquisition

class ResourceCollector(collector.ResourceCollector, Acquisition.Implicit):

    def _get_request(self):
        return self.request

    def _get_managers(self):
        return [(name, manager.__of__(self)) for name, manager in \
                    super(ResourceCollector, self)._get_managers()]


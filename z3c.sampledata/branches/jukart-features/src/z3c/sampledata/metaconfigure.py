from zope import component
from zope.component.zcml import utility

from manager import Manager
from interfaces import ISampleManager


class sampleManager(object):

    def __init__(self,_context, name, seed=''):
        self.manager = Manager(name, seed)
        utility(_context, ISampleManager, component=self.manager, name=name)

    def generator(self, _context, name, dependsOn=None, contextFrom=None):
        dependencies = []
        if dependsOn is not None:
            dependencies = dependsOn.split(' ')
        self.manager.add(name, dependencies, contextFrom)

    def __call__(self):
        return


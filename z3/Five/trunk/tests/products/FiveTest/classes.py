from zope.interface import implements
from interfaces import IAdaptable, IAdapted

class Adaptable:
    implements(IAdaptable)

    def method(self):
        return "The method"
    
class Adapter:
    implements(IAdapted)
  
    def __init__(self, context):
        self.context = context
        
    def adaptedMethod(self):
        return "Adapted: %s" % self.context.method()

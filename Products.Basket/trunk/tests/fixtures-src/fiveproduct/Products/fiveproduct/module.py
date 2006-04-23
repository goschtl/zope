# test implementations

from zope.interface import Interface
from zope.interface import implements

class ISampleAdapter(Interface):
    pass

class SampleAdapter(object):
    implements(ISampleAdapter)
    def __init__(self, context):
        self.context = context

class IExtraSampleAdapter(Interface):
    pass

class ExtraSampleAdapter(object):
    implements(IExtraSampleAdapter)
    def __init__(self, context):
        self.context = context
        
    

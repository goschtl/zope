from zope import interface, component
import interfaces
import traversing
from zope.publisher.interfaces.browser import IBrowserRequest

@component.adapter(IBrowserRequest)
@interface.implementer(interfaces.ITraversalStackInfo)
def requestTraversalStackInfo(request):
    cons = request.annotations.get(traversing.ANNOTATION_KEY, [])
    return TraversalStackInfo(cons)

class TraversalStackInfo(tuple):
    interface.implements(interfaces.ITraversalStackInfo)

class BaseConsumer(object):
    interface.implements(interfaces.ITraversalStackConsumer)

    arguments = ()
    __name__ = None

    def __init__(self, context, request):
        self.context=context
        self.request=request

    def consume(self):
        stack = self.request.getTraversalStack()
        self.__name__ = stack.pop()
        for name in self.arguments:
            setattr(self, name, stack.pop())
        self.request.setTraversalStack(stack)

    def __repr__(self):
        return '<%s named %r>' % (self.__class__.__name__,
                                  self.__name__)

    

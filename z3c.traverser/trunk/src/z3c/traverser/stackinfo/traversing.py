from zope import component
import interfaces
from zope.publisher.interfaces import NotFound

ANNOTATION_KEY='z3c.traverser.consumers'

def getStackConsumers(context, request):
    """consumes the stack"""
    while True:
        stack = request.getTraversalStack() 
        if not stack:
            break
        name = stack[-1]
        consumer = component.queryMultiAdapter(
            (context, request),
            interface=interfaces.ITraversalStackConsumer,
            name=name)
        if consumer is not None:
            try:
                consumer.consume()
            except IndexError:
                raise NotFound(context, name, request)
            yield (name, consumer)
            continue
        break

def applyStackConsumers(context, request):
    cons = [cons for name, cons in getStackConsumers(context, request)]
    request.annotations[ANNOTATION_KEY] = cons

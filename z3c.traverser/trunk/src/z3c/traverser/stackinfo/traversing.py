from zope import component
import interfaces
from zope.publisher.interfaces import NotFound
from zope.traversing.browser.absoluteurl import absoluteURL
import urllib
from zope.publisher.browser import BrowserView

CONSUMERS_ANNOTATION_KEY='z3c.traverser.consumers'
CONSUMED_ANNOTATION_KEY='z3c.traverser.consumed'

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
    if not request.annotations.has_key(CONSUMED_ANNOTATION_KEY):
        request.annotations[CONSUMED_ANNOTATION_KEY] = []
        request.annotations[CONSUMERS_ANNOTATION_KEY] = []
    else:
        for obj, consumed in request.annotations[CONSUMED_ANNOTATION_KEY]:
            if obj == context:
                return
    orgStack = request.getTraversalStack()
    cons = [cons for name, cons in getStackConsumers(
        context, request)]
    newStack = request.getTraversalStack()
    if newStack != orgStack:
        consumed = request.annotations[CONSUMED_ANNOTATION_KEY]
        items = orgStack[len(newStack):]
        items.reverse()
        consumed.append((context, items))
    request.annotations[CONSUMERS_ANNOTATION_KEY].extend(cons)

def _encode(v, _safe='@+'):
    return urllib.quote(v.encode('utf-8'), _safe)

def unconsumedURL(context, request):
    
    consumed = list(request.annotations.get(CONSUMED_ANNOTATION_KEY))
    if not consumed:
        return absoluteURL(context, request)
    from zope.traversing import api

    from zope.traversing.interfaces import IContainmentRoot
    name = api.getName(context)
    items = name and [name] or []
    for obj, names in consumed:
        if obj == context:
            items.extend(names)
            break
    if IContainmentRoot.providedBy(context):
        base = absoluteURL(context, request)
    else:
        base = unconsumedURL(api.getParent(context), request)
    items = map(_encode, items)
    if not base.endswith('/'):
        base += '/'
    return base + '/'.join(items)

class UnconsumedURL(BrowserView):
    # XXX test this
    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        return unconsumedURL(self.context, self.request)

    __call__ = __str__
            
    
    
    

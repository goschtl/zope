from zope import interface
from zope import component

from z3c.indexing.dispatch.interfaces import IDispatcher
from z3c.indexing.dispatch import operation

from queue import index_queue as queue

class AsynchronousProcess(object):
    def __init__(self, operation, dispatcher):
        self.operation = operation
        self.dispatcher = dispatcher

    def dispatch(self):
        self.operation.process(self.dispatcher)

class AsynchronousDispatcher(object):
    """Asynchronous indexing dispatcher."""

    interface.implements(IDispatcher)

    def index(self, obj, attributes=None):
        self._enqueue(operation.Add(obj, attributes))
        
    def reindex(self, obj, attributes=None):
        self._enqueue(operation.Modify(obj, attributes))

    def unindex(self, obj):
        self._enqueue(operation.Delete(obj, attributes))

    def flush(self):
        queue.put(None)

    def _enqueue(self, op):
        obj = op.obj
        
        for name, dispatcher in component.getAdapters((self, obj), IDispatcher):
            process = AsynchronousProcess(op, dispatcher)
            queue.put(process)

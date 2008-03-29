from zope import interface

from z3c.indexing.dispatch.interfaces import IDispatcher, ITransactionalDispatcher
from z3c.indexing.dispatch.constants import INDEX, REINDEX, UNINDEX

class MockDispatcherFactory(object):
    def __init__(self):
        self.queue = []
        self.dispatcher = MockDispatcher()
        
    def __call__(self, *args):
        self.dispatcher.queue = self.queue
        return self.dispatcher
        
class MockDispatcher(object):
    interface.implements(IDispatcher)

    def __init__(self):
        self.queue = []

    def index(self, obj, attributes=None):
        self.queue.append((INDEX, obj, attributes))

    def reindex(self, obj, attributes=None):
        self.queue.append((REINDEX, obj, attributes))

    def unindex(self, obj):
        self.queue.append((UNINDEX, obj, None))

    def flush(self):
        self.queue.append('flush')
        
class MockTransactionalDispatcher(MockDispatcher):
    interface.implements(ITransactionalDispatcher)

    processed = None
    _hook = lambda self: 42

    def index(self, obj, attributes=None):
        super(MockTransactionalDispatcher, self).index(obj, attributes)
        self._hook()

    def reindex(self, obj, attributes=None):
        super(MockTransactionalDispatcher, self).reindex(obj, attributes)
        self._hook()

    def unindex(self, obj):
        super(MockTransactionalDispatcher, self).unindex(obj)
        self._hook()

    def getState(self):
        return list(self.queue)

    def setState(self, state):
        self.queue = state

    def optimize(self):
        pass

    def commit(self):
        self.processed = self.queue
        self.clear()
        
    def clear(self):
        self.queue = []

    def __len__(self):
        return len(self.queue)

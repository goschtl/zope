from zope import interface
from zope import component

from threading import local

from zope.app.publication.interfaces import IEndRequestEvent

from ZODB.interfaces import IConnection

from z3c.indexing.dispatch.interfaces import IDispatcher
from z3c.indexing.dispatch.interfaces import ITransactionalDispatcher
from z3c.indexing.dispatch.interfaces import IQueueReducer
from z3c.indexing.dispatch.constants import INDEX, REINDEX, UNINDEX
from z3c.indexing.dispatch.transactions import QueueTM
from z3c.indexing.dispatch import operation

import transaction

from logging import getLogger
debug = getLogger('z3c.indexing.dispatch.queue').info

localQueue = None

@interface.implementer(ITransactionalDispatcher)
def getDispatcher():
    """Return a (thread-local) dispatcher, creating one if necessary."""
    
    global localQueue
    if localQueue is None:
        localQueue = TransactionalDispatcher()
    return localQueue

@component.adapter(IEndRequestEvent)
def commit(ev):
    getDispatcher().commit()

class TransactionalDispatcher(local):
    """An indexing queue."""

    interface.implements(ITransactionalDispatcher)

    tmhook = None
    
    def __init__(self):
        self.queue = []
    
    def index(self, obj, attributes=None):
        self.queue.append(operation.Add(obj, attributes))
        self._hook()

    def reindex(self, obj, attributes=None):
        self.queue.append(operation.Modify(obj, attributes))
        self._hook()

    def unindex(self, obj):
        self.queue.append(operation.Delete(obj))
        self._hook()

    def flush(self):
        return self.commit()

    def commit(self):
        self._optimize()

        dispatchers = set()

        for op, obj, attributes in self.queue:
            conn = IConnection(obj, None)
                
            if conn is not None:
                conn.open()
                
            for name, dispatcher in component.getAdapters((self, obj), IDispatcher):
                if op == INDEX:
                    dispatcher.index(obj, attributes)
                elif op == REINDEX:
                    dispatcher.reindex(obj, attributes)
                elif op == UNINDEX:
                    dispatcher.unindex(obj)
                else:
                    raise ValueError('Invalid queue operation code: %d' % op)

                dispatchers.add(dispatcher)
            
        self.clear()

        for dispatcher in dispatchers:
            dispatcher.flush()

        transaction.commit()
        
    def clear(self):
        debug('clearing %d queue item(s)', len(self.queue))
        del self.queue[:]
        self.tmhook = None

    def setState(self, state):
        self.queue = state

    def getState(self):
        return list(self.queue)

    def __len__(self):
        return len(self.queue)

    def _hook(self):
        """Register a hook into the transaction machinery.

        The indexing operations in the queue should be carried out if
        and only if the transaction to which they belong is committed.
        """

        if self.tmhook is None:
            self.tmhook = QueueTM(self).register
            
        self.tmhook()

    def _optimize(self):
        reducer = component.queryUtility(IQueueReducer)
        if reducer is not None:
            self.queue = reducer.optimize(self.queue)


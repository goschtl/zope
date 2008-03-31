from zope import interface

from transaction.interfaces import ISavepointDataManager
from transaction import get as getTransaction

from interfaces import ITransactionalDispatcher

from threading import local

class QueueSavepoint:
    """Transaction savepoints using the ITransactionalDispatcher interface."""

    def __init__(self, queue):
        self.queue = queue
        self.state = queue.getState()

    def rollback(self):
        self.queue.setState(self.state)

class QueueTM(local):
    """Transaction manager for the transactional dispatcher."""
    
    interface.implements(ISavepointDataManager)

    def __init__(self, queue):
        local.__init__(self)
        self.registered = False
        self.vote = False
        assert ITransactionalDispatcher.providedBy(queue), queue
        self.queue = queue

    def register(self):
        if not self.registered:
            getTransaction().join(self)
            self.registered = True
            
    def savepoint(self):
        return QueueSavepoint(self.queue)

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        pass

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        self.registered = False

    def tpc_abort(self, transaction):
        self.queue.clear()
        self.registered = False

    abort = tpc_abort

    def sortKey(self):
        return id(self)

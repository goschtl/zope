from zope import interface

from transaction.interfaces import ISavepointDataManager
from transaction import get as getTransaction

from ore.alchemist import Session

import soup

class Savepoint:
    """Transaction savepoint."""

    def rollback(self):
        raise NotImplementedError("Rollbacks are not implemented.")

class TransactionManager(object):
    """Transaction manager for the database session.

    This is used to synchronize relations to concrete items.    
    """
    
    interface.implements(ISavepointDataManager)

    def __init__(self, obj, uuid):
        self.registered = False
        self.vote = False
        self.obj = obj
        self.uuid = uuid
        
        session = Session()

        try:
            session._d_pending[uuid] = obj
        except AttributeError:
            session._d_pending = {uuid: obj}
        
    def register(self):
        if not self.registered:
            getTransaction().join(self)
            self.registered = True
            
    def savepoint(self):
        return Savepoint()

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        obj = self.obj
        uuid = self.uuid

        # unset pending state
        session = Session()
        del session._d_pending[uuid]

        # build instance
        instance = soup.lookup(uuid)

        # update attributes
        soup.update(instance, obj)
        
    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        self.registered = False

    def tpc_abort(self, transaction):
        # unset pending state
        session = Session()
        del session._d_pending[self.uuid]
        
        self.registered = False

    abort = tpc_abort

    def sortKey(self):
        return id(self)

def registerObject(obj, uuid):
    session = Session()

    try:
        pending = session._d_pending.keys()
    except AttributeError:
        pending = ()
    
    if obj not in pending:
        TransactionManager(obj, uuid).register()


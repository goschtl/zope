from IDataManager import IRollback
from Transaction import Transaction, Status

import zLOG

# XXX need to change asserts of transaction status into explicit checks
# that raise some exception

# XXX need lots of error checking

class TransactionManager(object):

    txn_factory = Transaction

    def __init__(self):
        pass

    def new(self):
        txn = self.txn_factory(self)
        zLOG.LOG("txn", zLOG.DEBUG, "%s: begin" % txn)
        return txn

    def commit(self, txn):
        assert txn._status is Status.ACTIVE
        prepare_ok = True
        zLOG.LOG("txn", zLOG.DEBUG, "%s: prepare" % txn)
        for r in txn._resources:
            if prepare_ok and not r.prepare(txn):
                prepare_ok = False
        txn._status = Status.PREPARED
        if prepare_ok:
            self._commit(txn)
        else:
            self.abort(txn)

    def _commit(self, txn):
        zLOG.LOG("txn", zLOG.DEBUG, "%s: commit" % txn)
        # finish the two-phase commit
        for r in txn._resources:
            r.commit(txn)
        txn._status = Status.COMMITTED

    def abort(self, txn):
        zLOG.LOG("txn", zLOG.DEBUG, "%s: abort" % txn)
        assert txn._status in (Status.ACTIVE, Status.PREPARED)
        for r in txn._resources:
            r.abort(txn)
        txn._status = Status.ABORTED

    def savepoint(self, txn):
        zLOG.LOG("txn", zLOG.DEBUG, "%s: savepoint" % txn)
        return Rollback([r.savepoint(txn) for r in txn._resources])

class Rollback(object):

    __implements__ = IRollback

    def __init__(self, resources):
        self._resources = resources

    def rollback(self):
        for r in self._resources:
            r.rollback()

# make the transaction manager visible to client code
import thread

class ThreadedTransactionManager(TransactionManager):

    def __init__(self):
        self._pool = {}

    def new(self):
        tid = thread.get_ident()
        txn = self._pool.get(tid)
        if txn is None:
            txn = super(ThreadedTransactionManager, self).new()
            self._pool[tid] = txn
        return txn

    def _commit(self, txn):
        tid = thread.get_ident()
        assert self._pool[tid] is txn
        super(ThreadedTransactionManager, self)._commit(txn)
        del self._pool[tid]

    def abort(self, txn):
        tid = thread.get_ident()
        assert self._pool[tid] is txn
        super(ThreadedTransactionManager, self).abort(txn)
        del self._pool[tid]
            

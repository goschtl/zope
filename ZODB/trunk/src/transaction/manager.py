import logging

from transaction.interfaces import *
from transaction.txn import Transaction, Status, Set

# XXX need to change asserts of transaction status into explicit checks
# that raise some exception

# XXX need lots of error checking

class AbstractTransactionManager(object):
    # base class to provide commit logic
    # concrete class must provide logger attribute
    
    def commit(self, txn):
        # commit calls _finishCommit() or abort()
        assert txn._status is Status.ACTIVE
        txn._status = Status.PREPARING
        prepare_ok = True
        self.logger.debug("%s: prepare", txn)
        try:
            for r in txn._resources:
                if prepare_ok and not r.prepare(txn):
                    prepare_ok = False
        except:
            txn._status = Status.FAILED
            raise
        txn._status = Status.PREPARED
        # XXX An error below is intolerable.  What state to use?
        if prepare_ok:
            self._finishCommit(txn)
        else:
            self.abort(txn)

    def _finishCommit(self, txn):
        self.logger.debug("%s: commit", txn)
        # finish the two-phase commit
        for r in txn._resources:
            r.commit(txn)
        txn._status = Status.COMMITTED

    def abort(self, txn):
        self.logger.debug("%s: abort", txn)
        assert txn._status in (Status.ACTIVE, Status.PREPARED, Status.FAILED)
        txn._status = Status.PREPARING
        for r in txn._resources:
            r.abort(txn)
        txn._status = Status.ABORTED

    def savepoint(self, txn):
        self.logger.debug("%s: savepoint", txn)
        return Rollback([r.savepoint(txn) for r in txn._resources])

class TransactionManager(AbstractTransactionManager):

    txn_factory = Transaction

    __implements__ = ITransactionManager

    def __init__(self):
        self.logger = logging.getLogger("txn")
        self._current = None

    def get(self):
        if self._current is None:
            self._current = self.begin()
        return self._current

    def begin(self):
        txn = self.txn_factory(self)
        self.logger.debug("%s: begin", txn)
        return txn

    def commit(self, txn):
        super(TransactionManager, self).commit(txn)
        self._current = None

    def abort(self, txn):
        super(TransactionManager, self).abort(txn)
        self._current = None

    # XXX need suspend and resume

class Rollback(object):

    __implements__ = IRollback

    def __init__(self, resources):
        self._resources = resources

    def rollback(self):
        for r in self._resources:
            r.rollback()

# make the transaction manager visible to client code
import thread

class ThreadedTransactionManager(AbstractTransactionManager):

    # XXX Do we need locking on _pool or _suspend?

    # Most methods read and write pool based on the id of the current
    # thread, so they should never interfere with each other.

    # The suspend() and resume() methods modify the _suspend set,
    # but suspend() only adds a new thread.  The resume() method
    # does need a lock to prevent two different threads from resuming
    # the same transaction.

    __implements__ = ITransactionManager

    def __init__(self):
        self.logger = logging.getLogger("txn")
        self._pool = {}
        self._suspend = Set()
        self._lock = thread.allocate_lock()

    def get(self):
        tid = thread.get_ident()
        txn = self._pool.get(tid)
        if txn is None:
            txn = self.begin()
        return txn

    def begin(self):
        tid = thread.get_ident()
        txn = self._pool.get(tid)
        if txn is not None:
            txn.abort()
        txn = self.txn_factory(self)
        self._pool[tid] = txn
        return txn

    def _finishCommit(self, txn):
        tid = thread.get_ident()
        assert self._pool[tid] is txn
        super(ThreadedTransactionManager, self)._finishCommit(txn)
        del self._pool[tid]

    def abort(self, txn):
        tid = thread.get_ident()
        assert self._pool[tid] is txn
        super(ThreadedTransactionManager, self).abort(txn)
        del self._pool[tid]

    # XXX should we require that the transaction calling suspend()
    # be the one that is using the transaction?

    # XXX need to add locking to suspend() and resume()

    def suspend(self, txn):
        tid = thread.get_ident()
        if self._pool[tid] is txn:
            self._suspend.add(txn)
            del self._pool[tid]
        else:
            raise TransactionError("txn %s not owned by thread %s" %
                                   (txn, tid))

    def resume(self, txn):
        tid = thread.get_ident()
        if self._pool.get(tid) is not None:
            raise TransactionError("thread %s already has transaction" %
                                   tid)
        if txn not in self._suspend:
            raise TransactionError("unknown transaction: %s" % txn)
        del self._suspend[txn]
        self._pool[tid] = txn

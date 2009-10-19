##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from bsddb3 import db
import os
import ZODB.POSException
import ZODB.TimeStamp


class BSDDBStorage:

    def __init__(self, envpath):
        self.__name__ = envpath
        if not os.path.isdir(envpath):
            os.mkdir(envpath)

        self.env = db.DBEnv()
        self.env.open(envpath,
                      db.DB_INIT_LOCK | db.DB_INIT_LOG | db.DB_INIT_MPOOL |
                      db.DB_INIT_TXN | db.DB_RECOVER | db.DB_THREAD |
                      db.DB_CREATE | db.DB_AUTO_COMMIT)

        # data: {oid -> [tid+data]}
        self.data = db.DB(self.env)
        self.data.set_flags(db.DB_DUP)
        self.data.open('data', dbtype=db.DB_HASH,
                       flags=(db.DB_CREATE | db.DB_THREAD | db.DB_AUTO_COMMIT |
                              db.DB_MULTIVERSION),
                       )
        self.datapath = os.path.abspath(os.path.join(envpath, 'data'))

        # transaction_oids: {tid->[oids]}
        self.transaction_oids = db.DB(self.env)
        self.transaction_oids.set_flags(db.DB_DUP)
        self.transaction_oids.open('transaction_oids', dbtype=db.DB_BTREE,
                                   flags=(db.DB_CREATE | db.DB_THREAD |
                                          db.DB_AUTO_COMMIT |
                                          db.DB_MULTIVERSION),
                                   )

        # transactions: {tid ->transaction_pickle}
        self.transactions = db.DB(self.env)
        self.transaction.open('transactions', dbtype=db.DB_BTREE,
                              flags=(db.DB_CREATE | db.DB_THREAD |
                                     db.DB_AUTO_COMMIT | db.DB_MULTIVERSION),
                              )

    def txn(self, flags=0):
        return TransactionContext(self.env.txn_begin(flags=flags))

    def cursor(self, db, txn=None, flags=0):
        return CursorContext(self.db.cursor(txn, flags))

    def close(self):
        self.data.close()
        self.transaction_oids.close()
        self.transactions.close()

    def getName(self):
        return self.__name__

    def getSize(self):
        return os.stat(self.datapath)

    def _history_entry(self, record, txn):
        tid = record[:8]
        transaction = cPickle.loads(self.transactions.get(tid, txn=txn))
        transaction.update(size=len(record-8))

    def history(self, oid, size=1):
        with self.txn(db.DB_TXN_SNAPSHOT) as txn:
            with self.cursor(self.data, txn) as cursor:
                k, record = cursor.get(oid, db.DB_PREV)
                if k != oid or len(record) == 8:
                    raise ZODB.POSException.POSKeyError(oid)

                result = [_history_entry(record)]
                while len(result) < size):
                    kv = cursor.get(oid, db.PREV_DUP)
                    if kv is None:
                        break
                    result.append(_history_entry(kb[1])

                cursor.close()
                return result

    def isReadOnly(self):
        return False

    def lastTransaction(self):
        with self.txn() as txn:
            with self.cursor(self.data, txn) as cursor:
                return cursor.get(db.DB_LAST)[0]

    def __len__(self):
        return self.data.stat(db.DB_FAST_STAT)['nkeys']

    def load(self, oid, version=''):
        with self.txn() as txn:
            with self.cursor(self.data, txn) as cursor:
                k, record = cursor.get(oid, db.DB_PREV)
                if k != oid or len(record) == 8:
                    raise ZODB.POSException.POSKeyError(oid)
                return result[8:], result[:8]


    def loadBefore(self, oid, tid):
        with self.txn(db.DB_TXN_SNAPSHOT) as txn:
            with self.cursor(self.data, txn) as cursor:
                k, record = cursor.get(oid, db.DB_PREV)
                if k != oid or len(record) == 8:
                    raise ZODB.POSException.POSKeyError(oid)
                nexttid = None
                rtid = record[:8]
                while rtid >= tid:
                    krecord = cursor.get(oid, db.PREV_DUP)
                    if krecord is None:
                        return None
                    nexttid = rtid
                    record = krecord[1]
                    rtid = record[:8]

                return record[8:], rtid, nexttid

    def loadSerial(oid, serial):
        with self.txn(db.DB_TXN_SNAPSHOT) as txn:
            with self.cursor(self.data, txn) as cursor:
                k, record = cursor.get(oid, db.DB_PREV)
                if k != oid or len(record) == 8:
                    raise ZODB.POSException.POSKeyError(oid)
                nexttid = None
                rtid = record[:8]
                while rtid >= tid:
                    krecord = cursor.get(oid, db.PREV_DUP)
                    if krecord is None:
                        return None
                    nexttid = rtid
                    record = krecord[1]
                    rtid = record[:8]

                return record[8:], rtid, nexttid



        """Load the object record for the give transaction id

        If a matching data record can be found, it is returned,
        otherwise, POSKeyError is raised.
        """

#     The following two methods are effectively part of the interface,
#     as they are generally needed when one storage wraps
#     another. This deserves some thought, at probably debate, before
#     adding them.
#
#     def _lock_acquire():
#         """Acquire the storage lock
#         """

#     def _lock_release():
#         """Release the storage lock
#         """

    def new_oid():
        """Allocate a new object id.

        The object id returned is reserved at least as long as the
        storage is opened.

        The return value is a string.
        """

    def pack(pack_time, referencesf):
        """Pack the storage

        It is up to the storage to interpret this call, however, the
        general idea is that the storage free space by:

        - discarding object revisions that were old and not current as of the
          given pack time.

        - garbage collecting objects that aren't reachable from the
          root object via revisions remaining after discarding
          revisions that were not current as of the pack time.

        The pack time is given as a UTC time in seconds since the
        epoch.

        The second argument is a function that should be used to
        extract object references from database records.  This is
        needed to determine which objects are referenced from object
        revisions.
        """

    def registerDB(db):
        """Register an IStorageDB.

        Note that, for historical reasons, an implementation may
        require a second argument, however, if required, the None will
        be passed as the second argument.
        """

    def sortKey():
        """Sort key used to order distributed transactions

        When a transaction involved multiple storages, 2-phase commit
        operations are applied in sort-key order.  This must be unique
        among storages used in a transaction. Obviously, the storage
        can't assure this, but it should construct the sort key so it
        has a reasonable chance of being unique.

        The result must be a string.
        """

    def store(oid, serial, data, version, transaction):
        """Store data for the object id, oid.

        Arguments:

        oid
            The object identifier.  This is either a string
            consisting of 8 nulls or a string previously returned by
            new_oid. 

        serial
            The serial of the data that was read when the object was
            loaded from the database.  If the object was created in
            the current transaction this will be a string consisting
            of 8 nulls.

        data
            The data record. This is opaque to the storage.

        version
            This must be an empty string. It exists for backward compatibility.

        transaction
            A transaction object.  This should match the current
            transaction for the storage, set by tpc_begin.

        The new serial for the object is returned, but not necessarily
        immediately.  It may be returned directly, or on a subsequent
        store or tpc_vote call.

        The return value may be:

        - None

        - A new serial (string) for the object, or

        - An iterable of object-id and serial pairs giving new serials
          for objects.

        A serial, returned as a string or in a sequence of oid/serial
        pairs, may be the special value
        ZODB.ConflictResolution.ResolvedSerial to indicate that a
        conflict occured and that the object should be invalidated.

        Several different exceptions may be raised when an error occurs.

        ConflictError
          is raised when serial does not match the most recent serial
          number for object oid and the conflict was not resolved by
          the storage.

        StorageTransactionError
          is raised when transaction does not match the current
          transaction.

        StorageError or, more often, a subclass of it
          is raised when an internal error occurs while the storage is
          handling the store() call.
        
        """

    def tpc_abort(transaction):
        """Abort the transaction.

        Any changes made by the transaction are discarded.

        This call is ignored is the storage is not participating in
        two-phase commit or if the given transaction is not the same
        as the transaction the storage is commiting.
        """

    def tpc_begin(transaction):
        """Begin the two-phase commit process.

        If storage is already participating in a two-phase commit
        using the same transaction, the call is ignored.

        If the storage is already participating in a two-phase commit
        using a different transaction, the call blocks until the
        current transaction ends (commits or aborts).
        """

    def tpc_finish(transaction, func = lambda tid: None):
        """Finish the transaction, making any transaction changes permanent.

        Changes must be made permanent at this point.

        This call is ignored if the storage isn't participating in
        two-phase commit or if it is committing a different
        transaction.  Failure of this method is extremely serious.

        The second argument is a call-back function that must be
        called while the storage transaction lock is held.  It takes
        the new transaction id generated by the transaction.

        """

    def tpc_vote(transaction):
        """Provide a storage with an opportunity to veto a transaction

        This call is ignored if the storage isn't participating in
        two-phase commit or if it is commiting a different
        transaction.  Failure of this method is extremely serious.

        If a transaction can be committed by a storage, then the
        method should return.  If a transaction cannot be committed,
        then an exception should be raised.  If this method returns
        without an error, then there must not be an error if
        tpc_finish or tpc_abort is called subsequently.

        The return value can be either None or a sequence of object-id
        and serial pairs giving new serials for objects who's ids were
        passed to previous store calls in the same transaction.
        After the tpc_vote call, new serials must have been returned,
        either from tpc_vote or store for objects passed to store.

        A serial returned in a sequence of oid/serial pairs, may be
        the special value ZODB.ConflictResolution.ResolvedSerial to
        indicate that a conflict occured and that the object should be
        invalidated.

        """



class TransactionContext(object):

    def __init__(self, txn):
        self.txn = txn

    def __enter__(self):
        return self.txn

    def __exit__(self, t, v, tb):
        if t is not None:
            self.txn.abort()
        else:
            self.txn.commit()

class CursorContext(object):

    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self.cursor

    def __exit__(self, t, v, tb):
        self.cursor.close()


import BasicStorage, pickle
from ZODB import POSException

class UndoStorage(BasicStorage.BasicStorage):

    def checkSimpleTransactionalUndo(self):
        oid = self._storage.new_oid()
        revid = self._dostore(oid, data=23)
        revid = self._dostore(oid, revid=revid, data=24)
        revid = self._dostore(oid, revid=revid, data=25)
        # Now start an undo transaction
        self._storage.tpc_begin(self._transaction)
        oids = self._storage.transactionalUndo(revid, self._transaction)
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert len(oids) == 1
        assert oids[0] == oid
        data, revid = self._storage.load(oid, '')
        assert pickle.loads(data) == 24
        # Do another one
        self._storage.tpc_begin(self._transaction)
        oids = self._storage.transactionalUndo(revid, self._transaction)
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert len(oids) == 1
        assert oids[0] == oid
        data, revid = self._storage.load(oid, '')
        assert pickle.loads(data) == 23
        # Try to undo the first record
        self._storage.tpc_begin(self._transaction)
        oids = self._storage.transactionalUndo(revid, self._transaction)
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert len(oids) == 1
        assert oids[0] == oid
        # This should fail since we've undone the object's creation
        self.assertRaises(KeyError,
                          self._storage.load, oid, '')
        # But it's really a more specific type of error
        import Full
        self.assertRaises(Full.ObjectDoesNotExist,
                          self._storage.load, oid, '')
        # And now let's try to redo the object's creation
        try:
            self._storage.load(oid, '')
        except Full.ObjectDoesNotExist, e:
            revid = e.revid
        self._storage.tpc_begin(self._transaction)
        oids = self._storage.transactionalUndo(revid, self._transaction)
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert len(oids) == 1
        assert oids[0] == oid
        data, revid = self._storage.load(oid, '')
        assert pickle.loads(data) == 23

    def checkTwoObjectUndo(self):
        # Convenience
        p31, p32, p51, p52 = map(pickle.dumps, (31, 32, 51, 52))
        oid1 = self._storage.new_oid()
        oid2 = self._storage.new_oid()
        revid1 = revid2 = ZERO
        # Store two objects in the same transaction
        self._storage.tpc_begin(self._transaction)
        revid1 = self._storage.store(oid1, revid1, p31, '', self._transaction)
        revid2 = self._storage.store(oid2, revid2, p51, '', self._transaction)
        # Finish the transaction
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert revid1 == revid2
        # Update those same two objects
        self._storage.tpc_begin(self._transaction)
        revid1 = self._storage.store(oid1, revid1, p32, '', self._transaction)
        revid2 = self._storage.store(oid2, revid2, p52, '', self._transaction)
        # Finish the transaction
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert revid1 == revid2
        # Make sure the objects have the current value
        data, revid1 = self._storage.load(oid1, '')
        assert pickle.loads(data) == 32
        data, revid2 = self._storage.load(oid2, '')
        assert pickle.loads(data) == 52
        # Now attempt to undo the transaction containing two objects
        self._storage.tpc_begin(self._transaction)
        oids = self._storage.transactionalUndo(revid1, self._transaction)
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert len(oids) == 2
        assert oid1 in oids and oid2 in oids
        data, revid1 = self._storage.load(oid1, '')
        assert pickle.loads(data) == 31
        data, revid2 = self._storage.load(oid2, '')
        assert pickle.loads(data) == 51

    def checkTwoObjectUndoAgain(self):
        p32, p33, p52, p53 = map(pickle.dumps, (32, 33, 52, 53))
        # Like the above, but the first revision of the objects are stored in
        # different transactions.
        oid1 = self._storage.new_oid()
        oid2 = self._storage.new_oid()
        revid1 = self._dostore(oid1, data=31)
        revid2 = self._dostore(oid2, data=51)
        # Update those same two objects
        self._storage.tpc_begin(self._transaction)
        revid1 = self._storage.store(oid1, revid1, p32, '', self._transaction)
        revid2 = self._storage.store(oid2, revid2, p52, '', self._transaction)
        # Finish the transaction
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert revid1 == revid2
        # Now attempt to undo the transaction containing two objects
        self._storage.tpc_begin(self._transaction)
        oids = self._storage.transactionalUndo(revid1, self._transaction)
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert len(oids) == 2
        assert oid1 in oids and oid2 in oids
        data, revid1 = self._storage.load(oid1, '')
        assert pickle.loads(data) == 31
        data, revid2 = self._storage.load(oid2, '')
        assert pickle.loads(data) == 51
        # Like the above, but this time, the second transaction contains only
        # one object.
        self._storage.tpc_begin(self._transaction)
        revid1 = self._storage.store(oid1, revid1, p33, '', self._transaction)
        revid2 = self._storage.store(oid2, revid2, p53, '', self._transaction)
        # Finish the transaction
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert revid1 == revid2
        # Update in different transactions
        revid1 = self._dostore(oid1, revid=revid1, data=34)
        revid2 = self._dostore(oid2, revid=revid2, data=54)
        # Now attempt to undo the transaction containing two objects
        self._storage.tpc_begin(self._transaction)
        oids = self._storage.transactionalUndo(revid1, self._transaction)
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert len(oids) == 1
        assert oid1 in oids and not oid2 in oids
        data, revid1 = self._storage.load(oid1, '')
        assert pickle.loads(data) == 33
        data, revid2 = self._storage.load(oid2, '')
        assert pickle.loads(data) == 54

    def checkNotUndoable(self):
        # Set things up so we've got a transaction that can't be undone
        oid = self._storage.new_oid()
        revid_a = self._dostore(oid, data=51)
        revid_b = self._dostore(oid, revid=revid_a, data=52)
        revid_c = self._dostore(oid, revid=revid_b, data=53)
        # Start the undo
        self._storage.tpc_begin(self._transaction)
        self.assertRaises(POSException.UndoError,
                          self._storage.transactionalUndo,
                          revid_b, self._transaction)
        self._storage.tpc_abort(self._transaction)
        # Now have more fun: object1 and object2 are in the same transaction,
        # which we'll try to undo to, but one of them has since modified in
        # different transaction, so the undo should fail.
        oid1 = oid
        revid1 = revid_c
        oid2 = self._storage.new_oid()
        revid2 = ZERO
        p81, p82, p91, p92 = map(pickle.dumps, (81, 82, 91, 92))
        self._storage.tpc_begin(self._transaction)
        revid1 = self._storage.store(oid1, revid1, p81, '', self._transaction)
        revid2 = self._storage.store(oid2, revid2, p91, '', self._transaction)
        self._storage.tpc_vote(self._transaction)
        self._storage.tpc_finish(self._transaction)
        assert revid1 == revid2
        # Make sure the objects have the expected values
        data, revid_11 = self._storage.load(oid1, '')
        assert pickle.loads(data) == 81
        data, revid_22 = self._storage.load(oid2, '')
        assert pickle.loads(data) == 91
        assert revid_11 == revid1 and revid_22 == revid2
        # Now modify oid2
        revid2 = self._dostore(oid2, revid=revid2, data=p92)
        assert revid1 <> revid2 and revid2 <> revid_22
        self._storage.tpc_begin(self._transaction)
        self.assertRaises(POSException.UndoError,
                          self._storage.transactionalUndo,
                          revid1, self._transaction)
        self.assertRaises(POSException.UndoError,
                          self._storage.transactionalUndo,
                          revid_22, self._transaction)
        self._storage.tpc_abort(self._transaction)

##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Transaction management

$Id: _defaultTransaction.py,v 1.7 2002/12/19 21:45:27 tim_one Exp $
"""
import sys
import logging

from Transaction.Exceptions import ConflictError, TransactionError

logger = logging.getLogger("Transaction")

# Flag indicating whether certain errors have occurred.
hosed = 0

already_hosed_text =  \
           """A serious error, which was probably a system error,
           occurred in a previous database transaction.  This
           application may be in an invalid state and must be
           restarted before database updates can be allowed.

           Beware though that if the error was due to a serious system
           problem, such as a disk full condition, then the
           application may not come up until you deal with the system
           problem.  See your application log for information on the
           error that lead to this problem.
           """

hosed_text = \
           """A storage error occurred in the last phase of a
           two-phase commit.  This shouldn't happen.  The application
           may be in a hosed state, so transactions will not be
           allowed to commit until the site/storage is reset by a
           restart.  """


class Transaction:
    """Simple transaction objects for single-threaded applications."""

    user = ""
    description = ""
    _connections = None
    _extension = None
    _sub = None # This is a subtrasaction flag

    # The _non_st_objects variable is either None or a list
    # of jars that do not support subtransactions. This is used to
    # manage non-subtransaction-supporting jars during subtransaction
    # commits and aborts to ensure that they are correctly committed
    # or aborted in the "outside" transaction.
    _non_st_objects = None

    def __init__(self, id=None):
        self._id = id
        self._objects = []

    def _init(self):
        self._objects = []
        self.user = self.description = ""
        if self._connections:
            for c in self._connections.values():
                c.close()
            del self._connections

    def sub(self):
        # Create a manually managed subtransaction for internal use
        r = self.__class__()
        r.user = self.user
        r.description = self.description
        r._extension = self._extension
        return r

    def __str__(self):
        return "Transaction %s %s" % (self._id or 0, self.user)

    def __del__(self):
        if self._objects:
            self.abort(freeme=0)

    def abort(self, subtransaction=0, freeme=1):
        """Abort the transaction.

        This is called from the application.  This means that we haven't
        entered two-phase commit yet, so no tpc_ messages are sent.
        """
        if subtransaction and (self._non_st_objects is not None):
            raise TransactionError, (
                """Attempted to abort a sub-transaction, but a participating
                data manager doesn't support partial abort.
                """)

        t = None
        subj = self._sub
        subjars = ()

        if not subtransaction:

            # Must add in any non-subtransaction supporting objects that
            # may have been stowed away from previous subtransaction
            # commits.
            if self._non_st_objects is not None:
                self._objects.extend(self._non_st_objects)
                self._non_st_objects = None

            if subj is not None:
                # Abort of top-level transaction after commiting
                # subtransactions.
                subjars = subj.values()
                self._sub = None

        try:
            # Abort the objects
            for o in self._objects:
                try:
                    j = getattr(o, '_p_jar', o)
                    if j is not None:
                        j.abort(o, self)
                except:
                    if t is None:
                        t, v, tb = sys.exc_info()

            # Ugh, we need to abort work done in sub-transactions.
            while subjars:
                j = subjars.pop()
                j.abort_sub(self) # This should never fail

            if t is not None:
                raise t, v, tb

        finally:
            if t is not None:
                del tb # don't keep traceback in local variable
            del self._objects[:] # Clear registered
            if not subtransaction and freeme:
                if self._id is not None:
                    free_transaction()
            else:
                self._init()

    def begin(self, info=None, subtransaction=None):
        """Begin a new transaction.

        This aborts any transaction in progres.
        """
        if self._objects:
            self.abort(subtransaction, 0)
        if info:
            info = info.split("\t")
            self.user = info[0].strip()
            self.description = ("\t".join(info[1:])).strip()

    def commit(self, subtransaction=None):
        """Finalize the transaction."""

        # This method does all the setup, then calls _commit().

        global hosed

        # Make local reference to objects, which will be changed to
        # new object if there is an implicit subtransaction commit
        objects = self._objects
        jars = {}
        jarsv = None
        subjars = ()

        if subtransaction:
            if self._sub is None:
                self._sub = {}
        else:
            if self._sub is not None:
                if objects:
                    # Do an implicit sub-transaction commit:
                    self.commit(1)
                    objects = []
                subjars = self._sub.values()
                self._sub = None

        # If not a subtransaction, then we need to add any non-
        # subtransaction-supporting objects that may have been
        # stowed away during subtransaction commits to _objects.
        if (subtransaction is None) and (self._non_st_objects is not None):
            objects.extend(self._non_st_objects)
            self._non_st_objects = None

        t = v = tb = None

        if (objects or subjars) and hosed:
            # Something really bad happened and we don't
            # trust the system state.
            raise TransactionError(already_hosed_text)

        try:
            self._commit(objects, jars, subtransaction, subjars)
        finally:
            tb = None
            del objects[:] # clear registered
            if not subtransaction and self._id is not None:
                free_transaction()

    def _commit(self, objects, jars, subtransaction, subjars):
        # Do the real work of commit

        # It's important that:
        #
        # - Every object in self._objects is either committed
        #   or aborted.
        #
        # - For each object that is committed
        #   we call tpc_begin on its jar at least once
        #
        # - For every jar for which we've called tpc_begin on,
        #   we either call tpc_abort or tpc_finish. It is OK
        #   to call these multiple times, as the storage is
        #   required to ignore these calls if tpc_begin has not
        #   been called.

        ncommitted = 0
        jarsv = None
        try:
            for o in objects:
                j = getattr(o, '_p_jar', o)
                if j is None:
                    logger.error("Ignoring object %s because it has no jar",
                                 repr(o))
                else:
                    if __debug__:
                        logger.error("Committing %s with jar %s", repr(o), j)
                    i = id(j)
                    if i not in jars:
                        jars[i] = j

                        if subtransaction:
                            if not self._subtrans_begin(o, j, subtransaction):
                                # The jar does not support subtransactions
                                continue
                        else:
                            j.tpc_begin(self)
                    j.commit(o, self)
                ncommitted += 1

            jars.update(self._subtrans_commit(subjars))

            jarsv = jars.values()
            for jar in jarsv:
                if not subtransaction:
                    jar.tpc_vote(self)

            # commit one first, because we can still recover if only
            # the first one fails
            self._commit_one(jarsv)
            self._commit_rest(jarsv)
        except:
            t, v, tb = sys.exc_info()

            if jarsv is None:
                cleanup_jars = jars.values()
            else:
                cleanup_jars = jarsv
            self._commit_failed(objects[ncommitted:], cleanup_jars, subjars)

            raise t, v, tb

    def _commit_one(self, jarsv):
        try:
            # Try to finish one jar, since we may be able to recover
            # if the first one fails.
            if jarsv:
                jarsv[-1].tpc_finish(self) # This should never fail
                jarsv.pop() # It didn't, so it's taken care of.
        except:
            # Bug if it does, we need to keep track of it
            logger.error("A storage error occurred in the last phase of a "
                         "two-phase commit.  This shouldn\'t happen. ",
                         exc_info=True)
            raise

    def _commit_rest(self, jarsv):
        global hosed
        try:
            while jarsv:
                jarsv[-1].tpc_finish(self) # This should never fail
                jarsv.pop() # It didn't, so it's taken care of.
        except:
            # But if it does, we need to yell FIRE!  Someone finished,
            # so don't allow any more work without at least a restart!
            hosed = 1
            logger.critical(hosed_text, exc_info=True)
            raise

    def _commit_failed(self, uncommitted, jarsv, subjars):
        # Ugh, we got an got an error during commit, so we have to
        # clean up.

        # First, we have to abort any uncommitted objects.
        for o in uncommitted:
            try:
                j = getattr(o, '_p_jar', o)
                if j is not None:
                    j.abort(o, self)
            except:
                logger.error(
                    "An error occured while cleaning up a failed commit.",
                    exc_info=True)

        # Then, we unwind TPC for the jars that began it.
        for j in jarsv:
            try:
                j.tpc_abort(self) # This should never fail
            except:
                logger.error("A storage error occured during object abort "
                             "This shouldn't happen. ",
                             exc_info=True)

        # Ugh, we need to abort work done in sub-transactions.
        for j in subjars:
            j.abort_sub(self) # This should never fail
            # XXX Shouldn't we have a try-except anyway?

    def _subtrans_begin(self, obj, jar, subtransaction):
        # If a jar does not support subtransactions, we need to save
        # it away to be committed in the outer transaction.

        # XXX I think subtransaction is always 1, and, thus, doesn't
        # need to be passed
        assert subtransaction == 1
        try:
            jar.tpc_begin(self, subtransaction)
        except TypeError:
            jar.tpc_begin(self)

        if hasattr(jar, 'commit_sub'):
            self._sub[id(jar)] = jar
            return 1
        else:
            if self._non_st_objects is None:
                self._non_st_objects = []
            self._non_st_objects.append(obj)
            return 0

    def _subtrans_commit(self, subjars):
        jars = {}
        # Commit work done in subtransactions
        while subjars:
            j = subjars.pop()
            jars[id(j)] = j
            j.commit_sub(self)
        return jars

    def register(self, object):
        """Register the given object for transaction control."""

        self._objects.append(object)

    def note(self, text):
        if self.description:
            self.description = "%s\n\n%s" % (self.description, text.strip())
        else:
            self.description = text.strip()

    def setUser(self, user_name, path='/'):
        self.user = "%s %s" % (path, user_name)

    def setExtendedInfo(self, name, value):
        if self._extension is None:
            self._extension = {}
        self._extension[name] = value


############################################################################
# install get_transaction:

try:
    import thread
except:
    _t = Transaction(None)

    def get_transaction():
        return _t

    def free_transaction():
        _t.__init__()

else:
    _t = {}
    def get_transaction():
        id = thread.get_ident()
        t = _t.get(id)
        if t is None:
            _t[id] = t = Transaction(id)
        return t

    def free_transaction():
        id = thread.get_ident()
        try:
            del _t[id]
        except KeyError:
            pass

__all__ = ["Transaction", "get_transaction", "free_transaction"]

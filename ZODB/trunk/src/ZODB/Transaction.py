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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Transaction management

$Id: Transaction.py,v 1.38 2002/09/11 18:41:24 jeremy Exp $"""
__version__='$Revision: 1.38 $'[11:-2]

import time, sys, struct, POSException
from struct import pack
from string import split, strip, join
from zLOG import LOG, ERROR, PANIC
from POSException import ConflictError

# Flag indicating whether certain errors have occurred.
hosed=0

class Transaction:
    'Simple transaction objects for single-threaded applications.'
    user=''
    description=''
    _connections=None
    _extension=None
    _sub=None # This is a subtrasaction flag

    # The _non_st_objects variable is either None or a list
    # of jars that do not support subtransactions. This is used to
    # manage non-subtransaction-supporting jars during subtransaction
    # commits and aborts to ensure that they are correctly committed
    # or aborted in the "outside" transaction.
    _non_st_objects=None

    def __init__(self, id=None):
        self._id=id
        self._objects=[]
        self._append=self._objects.append

    def _init(self):
        self._objects=[]
        self._append=self._objects.append
        self.user=self.description=''
        if self._connections:
            for c in self._connections.values(): c.close()
            del self._connections

    def sub(self):
        # Create a manually managed subtransaction for internal use
        r=self.__class__()
        r.user=self.user
        r.description=self.description
        r._extension=self._extension
        return r

    def __str__(self):
        if self._id is None:
            return "Transaction user=%s" % `self.user`
        else:
            return "Transaction thread=%s user=%s" % (self._id, `self.user`)

    def __del__(self):
        if self._objects: self.abort(freeme=0)

    def abort(self, subtransaction=0, freeme=1):
        '''Abort the transaction.

        This is called from the application.  This means that we haven\'t
        entered two-phase commit yet, so no tpc_ messages are sent.
        '''

        if subtransaction and (self._non_st_objects is not None):
            raise POSException.TransactionError, (
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
        '''Begin a new transaction.

        This aborts any transaction in progres.
        '''
        if self._objects: self.abort(subtransaction, 0)
        if info:
            info=split(info,'\t')
            self.user=strip(info[0])
            self.description=strip(join(info[1:],'\t'))

    def commit(self, subtransaction=None):
        'Finalize the transaction'

        objects = self._objects
        jars = {}
        jarsv = None
        subj = self._sub
        subjars = ()

        if subtransaction:
            if subj is None:
                self._sub = subj = {}
        else:
            if subj is not None:
                if objects:
                    # Do an implicit sub-transaction commit:
                    self.commit(1)
                    # XXX What does this do?
                    objects = []
                subjars = subj.values()
                self._sub = None

        # If not a subtransaction, then we need to add any non-
        # subtransaction-supporting objects that may have been
        # stowed away during subtransaction commits to _objects.
        if (subtransaction is None) and (self._non_st_objects is not None):
            objects.extend(self._non_st_objects)
            self._non_st_objects = None

        if (objects or subjars) and hosed:
            # Something really bad happened and we don't
            # trust the system state.
            raise POSException.TransactionError, hosed_msg

        # It's important that:
        #
        # - Every object in self._objects is either committed or
        #   aborted.
        #
        # - For each object that is committed we call tpc_begin on
        #   it's jar at least once
        #
        # - For every jar for which we've called tpc_begin on, we
        #   either call tpc_abort or tpc_finish. It is OK to call
        #   these multiple times, as the storage is required to ignore
        #   these calls if tpc_begin has not been called.
        try:
            ncommitted = 0
            try:
                ncommitted += self._commit_objects(objects, jars,
                                                   subtransaction, subj)

                self._commit_subtrans(jars, subjars)

                jarsv = jars.values()
                for jar in jarsv:
                    if not subtransaction:
                        try:
                            vote = jar.tpc_vote
                        except:
                            pass
                        else:
                            vote(self) # last chance to bail

                # Handle multiple jars separately.  If there are
                # multiple jars and one fails during the finish, we
                # mark this transaction manager as hosed.
                if len(jarsv) == 1:
                    self._finish_one(jarsv[0])
                else:
                    self._finish_many(jarsv)
            except:
                # Ugh, we got an got an error during commit, so we
                # have to clean up.
                exc_info = sys.exc_info()
                if jarsv is None:
                    jarsv = jars.values()
                self._commit_error(exc_info, objects, ncommitted,
                                   jarsv, subjars)
        finally:
            del objects[:] # clear registered
            if not subtransaction and self._id is not None:
                free_transaction()

    def _commit_objects(self, objects, jars, subtransaction, subj):
        # commit objects and return number of commits
        ncommitted = 0
        for o in objects:
            j = getattr(o, '_p_jar', o)
            if j is not None:
                i = id(j)
                if not jars.has_key(i):
                    jars[i] = j

                    if subtransaction:
                        # If a jar does not support subtransactions,
                        # we need to save it away to be committed in
                        # the outer transaction.
                        try:
                            j.tpc_begin(self, subtransaction)
                        except TypeError:
                            j.tpc_begin(self)

                        if hasattr(j, 'commit_sub'):
                            subj[i] = j
                        else:
                            if self._non_st_objects is None:
                                self._non_st_objects = []
                            self._non_st_objects.append(o)
                            continue
                    else:
                        j.tpc_begin(self)
                j.commit(o, self)
            ncommitted += 1
        return ncommitted

    def _commit_subtrans(self, jars, subjars):
        # Commit work done in subtransactions
        while subjars:
            j = subjars.pop()
            i = id(j)
            if not jars.has_key(i):
                jars[i] = j
            j.commit_sub(self)

    def _finish_one(self, jar):
        try:
            jar.tpc_finish(self) # This should never fail
        except:
            # Bug if it does, we need to keep track of it
            LOG('ZODB', ERROR,
                "A storage error occurred in the last phase of a "
                "two-phase commit.  This shouldn\'t happen. ",
                error=sys.exc_info())
            raise

    def _finish_many(self, jarsv):
        global hosed
        try:
            while jarsv:
                jarsv[-1].tpc_finish(self) # This should never fail
                jarsv.pop() # It didn't, so it's taken care of.
        except:
            # Bug if it does, we need to yell FIRE!
            # Someone finished, so don't allow any more
            # work without at least a restart!
            hosed = 1
            LOG('ZODB', PANIC,
                "A storage error occurred in the last phase of a "
                "two-phase commit.  This shouldn\'t happen. "
                "The application may be in a hosed state, so "
                "transactions will not be allowed to commit "
                "until the site/storage is reset by a restart. ",
                error=sys.exc_info())
            raise

    def _commit_error(self, (t, v, tb),
                      objects, ncommitted, jarsv, subjars):
        # handle an exception raised during commit
        # takes sys.exc_info() as argument

        # First, we have to abort any uncommitted objects.
        for o in objects[ncommitted:]:
            try:
                j = getattr(o, '_p_jar', o)
                if j is not None:
                    j.abort(o, self)
            except:
                pass

        # Then, we unwind TPC for the jars that began it.
        for j in jarsv:
            try:
                j.tpc_abort(self) # This should never fail
            except:
                LOG('ZODB', ERROR,
                    "A storage error occured during object abort. This "
                    "shouldn't happen. ", error=sys.exc_info())

        # Ugh, we need to abort work done in sub-transactions.
        while subjars:
            j = subjars.pop()
            try:
                j.abort_sub(self) # This should never fail
            except:
                LOG('ZODB', ERROR,
                    "A storage error occured during sub-transaction "
                    "object abort.  This shouldn't happen.",
                    error=sys.exc_info())

        raise t, v, tb

    def register(self,object):
        'Register the given object for transaction control.'
        self._append(object)

    def note(self, text):
        if self.description:
            self.description = "%s\n\n%s" % (self.description, strip(text))
        else:
            self.description = strip(text)

    def setUser(self, user_name, path='/'):
        self.user="%s %s" % (path, user_name)

    def setExtendedInfo(self, name, value):
        ext=self._extension
        if ext is None:
            ext=self._extension={}
        ext[name]=value

hosed_msg = \
"""A serious error, which was probably a system error,
occurred in a previous database transaction.  This
application may be in an invalid state and must be
restarted before database updates can be allowed.

Beware though that if the error was due to a serious
system problem, such as a disk full condition, then
the application may not come up until you deal with
the system problem.  See your application log for
information on the error that lead to this problem.
"""



############################################################################
# install get_transaction:

try:
    import thread

except:
    _t = Transaction(None)

    def get_transaction(_t=_t):
        return _t

    def free_transaction(_t=_t):
        _t.__init__()

else:
    _t = {}

    def get_transaction(_id=thread.get_ident, _t=_t, get=_t.get):
        id = _id()
        t = get(id, None)
        if t is None:
            _t[id] = t = Transaction(id)
        return t

    def free_transaction(_id=thread.get_ident, _t=_t):
        id = _id()
        try:
            del _t[id]
        except KeyError:
            pass

    del thread

del _t

import __main__
__main__.__builtins__.get_transaction=get_transaction

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
"""Provide a mixin base class for storage tests.

The StorageTestBase class provides basic setUp() and tearDown()
semantics (which you can override), and it also provides a helper
method _dostore() which performs a complete store transaction for a
single object revision.
"""

import sys
import time
import types
import unittest
from cPickle import Pickler, Unpickler
from cStringIO import StringIO

import transaction

from ZODB.utils import u64
from ZODB.tests.MinPO import MinPO

ZERO = '\0'*8

def snooze():
    # In Windows, it's possible that two successive time.time() calls return
    # the same value.  Tim guarantees that time never runs backwards.  You
    # usually want to call this before you pack a storage, or must make other
    # guarantees about increasing timestamps.
    now = time.time()
    while now == time.time():
        time.sleep(0.1)

def _persistent_id(obj):
    oid = getattr(obj, "_p_oid", None)
    if getattr(oid, "__get__", None) is not None:
        return None
    else:
        return oid

def zodb_pickle(obj):
    """Create a pickle in the format expected by ZODB."""
    f = StringIO()
    p = Pickler(f, 1)
    p.persistent_id = _persistent_id
    klass = obj.__class__
    assert not hasattr(obj, '__getinitargs__'), "not ready for constructors"
    args = None

    mod = getattr(klass, '__module__', None)
    if mod is not None:
        klass = mod, klass.__name__

    state = obj.__getstate__()

    p.dump((klass, args))
    p.dump(state)
    return f.getvalue(1)

def persistent_load(pid):
    # helper for zodb_unpickle
    return "ref to %s.%s oid=%s" % (pid[1][0], pid[1][1], u64(pid[0]))

def zodb_unpickle(data):
    """Unpickle an object stored using the format expected by ZODB."""
    f = StringIO(data)
    u = Unpickler(f)
    u.persistent_load = persistent_load
    klass_info = u.load()
    if isinstance(klass_info, types.TupleType):
        if isinstance(klass_info[0], type):
            # XXX what is the second part of klass_info?
            klass, xxx = klass_info
            assert not xxx
        else:
            if isinstance(klass_info[0], tuple):
                modname, klassname = klass_info[0]
            else:
                modname, klassname = klass_info
            if modname == "__main__":
                ns = globals()
            else:
                mod = import_helper(modname)
                ns = mod.__dict__
            try:
                klass = ns[klassname]
            except KeyError:
                print >> sys.stderr, "can't find %s in %r" % (klassname, ns)
        inst = klass()
    else:
        raise ValueError, "expected class info: %s" % repr(klass_info)
    state = u.load()
    inst.__setstate__(state)
    return inst

def handle_all_serials(oid, *args):
    """Return dict of oid to serialno from store() and tpc_vote().

    Raises an exception if one of the calls raised an exception.

    The storage interface got complicated when ZEO was introduced.
    Any individual store() call can return None or a sequence of
    2-tuples where the 2-tuple is either oid, serialno or an
    exception to be raised by the client.

    The original interface just returned the serialno for the
    object.
    """
    d = {}
    for arg in args:
        if isinstance(arg, types.StringType):
            d[oid] = arg
        elif arg is None:
            pass
        else:
            for oid, serial in arg:
                if not isinstance(serial, types.StringType):
                    raise serial # error from ZEO server
                d[oid] = serial
    return d

def handle_serials(oid, *args):
    """Return the serialno for oid based on multiple return values.

    A helper for function _handle_all_serials().
    """
    return handle_all_serials(oid, *args)[oid]

def import_helper(name):
    __import__(name)
    return sys.modules[name]


class StorageTestBase(unittest.TestCase):

    # XXX It would be simpler if concrete tests didn't need to extend
    # setUp() and tearDown().

    def setUp(self):
        # You need to override this with a setUp that creates self._storage
        self._storage = None

    def _close(self):
        # You should override this if closing your storage requires additional
        # shutdown operations.
        if self._storage is not None:
            self._storage.close()

    def tearDown(self):
        self._close()

    def _dostore(self, oid=None, revid=None, data=None, version=None,
                 already_pickled=0, user=None, description=None):
        """Do a complete storage transaction.  The defaults are:

         - oid=None, ask the storage for a new oid
         - revid=None, use a revid of ZERO
         - data=None, pickle up some arbitrary data (the integer 7)
         - version=None, use the empty string version

        Returns the object's new revision id.
        """
        if oid is None:
            oid = self._storage.new_oid()
        if revid is None:
            revid = ZERO
        if data is None:
            data = MinPO(7)
        if type(data) == types.IntType:
            data = MinPO(data)
        if not already_pickled:
            data = zodb_pickle(data)
        if version is None:
            version = ''
        # Begin the transaction
        t = transaction.Transaction()
        if user is not None:
            t.user = user
        if description is not None:
            t.description = description
        try:
            self._storage.tpc_begin(t)
            # Store an object
            r1 = self._storage.store(oid, revid, data, version, t)
            # Finish the transaction
            r2 = self._storage.tpc_vote(t)
            revid = handle_serials(oid, r1, r2)
            self._storage.tpc_finish(t)
        except:
            self._storage.tpc_abort(t)
            raise
        return revid

    def _dostoreNP(self, oid=None, revid=None, data=None, version=None,
                   user=None, description=None):
        return self._dostore(oid, revid, data, version, 1, user, description)

    # The following methods depend on optional storage features.

    def _undo(self, tid, expected_oids=None, note=None):
        # Undo a tid that affects a single object (oid).
        # XXX This is very specialized
        t = transaction.Transaction()
        t.note(note or "undo")
        self._storage.tpc_begin(t)
        tid, oids = self._storage.undo(tid, t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        if expected_oids is not None:
            self.assertEqual(len(oids), len(expected_oids), repr(oids))
            for oid in expected_oids:
                self.assert_(oid in oids)
        return self._storage.lastTransaction()

    def _commitVersion(self, src, dst):
        t = transaction.Transaction()
        t.note("commit %r to %r" % (src, dst))
        self._storage.tpc_begin(t)
        tid, oids = self._storage.commitVersion(src, dst, t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        return oids

    def _abortVersion(self, ver):
        t = transaction.Transaction()
        t.note("abort %r" % ver)
        self._storage.tpc_begin(t)
        tid, oids = self._storage.abortVersion(ver, t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        return oids

##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Extension of the ZODB Connection class

$Id$
"""

import sys
from time import time
from types import StringType, TupleType, DictType
from cStringIO import StringIO
from cPickle import Unpickler, Pickler

from Acquisition import aq_base
from Persistence import Persistent
from ZODB.Transaction import Transaction
from ZODB.POSException \
     import ConflictError, ReadConflictError, InvalidObjectReference, \
     StorageError
from ZODB.Connection import Connection
from ZODB.ConflictResolution import ResolvedSerial
from zLOG import LOG, ERROR

from consts import HASH0
from apelib.core.io import ObjectSystemIO
from apelib.core.interfaces import IObjectDatabase, LoadError


class ApeConnection (Connection):
    """Mapper-driven Connection

    Uses a mapper to serialize the state of objects before
    pickling, and to deserialize objects based on the pickled
    state.

    The mapper might, for example, serialize all objects as
    tabular records.
    """
    _osio = None
    _scan_ctl = None
    loaded_objects = False

    __implements__ = (IObjectDatabase,
                      getattr(Connection, '__implements__', ()))


    def _setDB(self, odb):
        Connection._setDB(self, odb)
        pool_ctl = odb.pool_scan_ctl
        if pool_ctl is not None:
            ctl = self._scan_ctl
            if ctl is None:
                self._scan_ctl = ctl = pool_ctl.new_connection()
            if ctl.elapsed():
                # Scan inside a transaction.
                get_transaction().register(self)
                # Let the scanner know which OIDs matter.
                ctl.set_oids(self._cache.cache_data.keys())
                # If it's time, scan on behalf of the whole pool.
                if pool_ctl.elapsed():
                    pool_ctl.scan()
                # If there were any invalidations, process them now.
                if self._invalidated:
                    self._flush_invalidations()


    def _prepare_root(self):
        osio = self._get_osio()
        oid = osio.conf.oid_gen.root_oid
        try:
            self[oid]
        except (KeyError, LoadError):
            # Create the root object.
            from Persistence import PersistentMapping
            root = PersistentMapping()
            root._p_jar = self
            root._p_changed = 1
            root._p_oid = oid
            t = Transaction()
            t.note('Initial database creation')
            self.tpc_begin(t)
            self.commit(root, t)
            self.tpc_vote(t)
            self.tpc_finish(t)

    def root(self):
        osio = self._get_osio()
        oid = osio.conf.oid_gen.root_oid
        return self[oid]

    def _get_osio(self):
        """Returns an ObjectSystemIO.
        """
        osio = self._osio
        if osio is None:
            conf = self._db._conf_resource.access(self)
            osio = ObjectSystemIO(conf, self)
            self._osio = osio
        return osio


    def close(self):
        db = self._db
        try:
            Connection.close(self)
        finally:
            if db is not None and self._osio is not None:
                self._osio = None
                db._conf_resource.release(self)


    def __getitem__(self, oid, tt=type(())):
        obj = self._cache.get(oid, None)
        if obj is not None:
            return obj

        __traceback_info__ = (oid)
        self.before_load()
        p, serial = self._storage.load(oid, self._version)
        __traceback_info__ = (oid, p)
        file=StringIO(p)
        unpickler=Unpickler(file)
        # unpickler.persistent_load=self._persistent_load

        try:
            classification = unpickler.load()
        except:
            raise ("Could not load oid %s. Pickled data in traceback info may "
                   "contain clues." % (oid))
        osio = self._get_osio()
        obj = osio.new_instance(oid, classification)
        assert obj is not None

        obj._p_oid=oid
        obj._p_jar=self
        obj._p_changed=None
        self._set_serial(obj, serial)

        self._cache[oid] = obj
        
        if oid == osio.conf.oid_gen.root_oid:
            self._root_=obj # keep a ref
        return obj


    def _persistent_load(self, oid, classification=None):

        __traceback_info__=oid

        obj = self._cache.get(oid, None)
        if obj is not None:
            return obj

        if classification:
            osio = self._get_osio()
            obj = osio.new_instance(oid, classification)
            if obj is not None:
                obj._p_oid=oid
                obj._p_jar=self
                obj._p_changed=None
                self._cache[oid] = obj
                return obj

        # We don't have enough info for fast loading.  Load the whole object.
        return self[oid]


    def _may_begin(self, transaction):
        if hasattr(self, '_begun') and not self._begun:
            self._storage.tpc_begin(transaction)
            self._begun = 1


    def commit(self, obj, transaction):
        if obj is self:
            self._may_begin(transaction)
            # We registered ourself.  Execute a commit action, if any.
            if self._Connection__onCommitActions is not None:
                method_name, args, kw = \
                             self._Connection__onCommitActions.pop(0)
                apply(getattr(self, method_name), (transaction,) + args, kw)
            return
        oid=obj._p_oid
        assert oid != 'unmanaged', repr(obj)
        #invalid=self._invalidated.get
        invalid = self._invalid

        modified = getattr(self, '_modified', None)
        if modified is None:
            modified = self._invalidating
        
        if oid is None or obj._p_jar is not self:
            # new object
            oid = self.new_oid()
            obj._p_jar=self
            obj._p_oid=oid
            self._creating.append(oid)

        elif obj._p_changed:
            if (
                (invalid(oid) and not hasattr(obj, '_p_resolveConflict'))
                or
                invalid(None)
                ):
                raise ConflictError(object=obj)
            modified.append(oid)

        else:
            # Nothing to do
            return

        self._may_begin(transaction)

        stack=[obj]

        file=StringIO()
        seek=file.seek
        pickler=Pickler(file,1)
        # SDH: external references are computed in a different way.
        # pickler.persistent_id=new_persistent_id(self, stack.append)
        dbstore=self._storage.store
        file=file.getvalue
        cache=self._cache
        get=cache.get
        dump=pickler.dump
        clear_memo=pickler.clear_memo


        version=self._version

        while stack:
            obj=stack[-1]
            del stack[-1]
            oid=obj._p_oid
            assert oid != 'unmanaged', repr(obj)
            serial = self._get_serial(obj)
            if serial == HASH0:
                # new object
                self._creating.append(oid)
            else:
                #XXX We should never get here
                # SDH: Actually it looks like we should, but only
                # for the first object on the stack.
                if (
                    (invalid(oid) and
                     not hasattr(obj, '_p_resolveConflict'))
                    or
                    invalid(None)
                    ):
                    raise ConflictError(object=obj)
                modified.append(oid)

            # SDH: hook in the serializer.
            # state=obj.__getstate__()
            osio = self._get_osio()
            event, classification, state = osio.serialize(oid, obj)
            ext_refs = event.external
            if ext_refs:
                for (ext_oid, ext_ref) in ext_refs:
                    assert ext_oid
                    assert ext_ref is not None
                    if self._cache.get(ext_oid, None) is not ext_ref:
                        # New object or a bad reference
                        if ext_ref._p_jar is not None:
                            if ext_ref._p_jar is not self:
                                raise InvalidObjectReference, (
                                    "Can't refer from %s in %s to %s in %s"
                                    % (repr(obj), repr(self), repr(ext_ref),
                                       repr(ext_ref._p_jar)))
                        else:
                            ext_ref._p_jar = self
                        if ext_ref._p_oid:
                            if ext_ref._p_oid != ext_oid:
                                raise StorageError('Conflicting OIDs')
                        else:
                            ext_ref._p_oid = ext_oid
                        stack.append(ext_ref)

            if event.upos:
                self._handle_unmanaged(obj, event.upos)

            seek(0)
            clear_memo()
            dump(classification)
            dump(state)
            p=file(1)
            s=dbstore(oid,serial,p,version,transaction)
            self._store_count = self._store_count + 1

            # Put the object in the cache before handling the
            # response, just in case the response contains the
            # serial number for a newly created object
            try: cache[oid] = obj
            except:
                if aq_base(obj) is not obj:
                    # Yuck, someone tried to store a wrapper.  Try to
                    # cache it unwrapped.
                    cache[oid] = aq_base(obj)
                else:
                    raise

            self._handle_serial(s, oid)


    def setstate(self, obj):
        oid=obj._p_oid

        self.before_load()
        try:
            p, serial = self._storage.load(oid, self._version)
            self._load_count = self._load_count + 1

            # XXX this is quite conservative!
            # We need, however, to avoid reading data from a transaction
            # that committed after the current "session" started, as
            # that might lead to mixing of cached data from earlier
            # transactions and new inconsistent data.
            #
            # Note that we (carefully) wait until after we call the
            # storage to make sure that we don't miss an invaildation
            # notifications between the time we check and the time we
            # read.
            #invalid = self._invalidated.get
            invalid = self._invalid
            if invalid(oid) or invalid(None):
                if not hasattr(obj.__class__, '_p_independent'):
                    get_transaction().register(self)
                    raise ReadConflictError(object=obj)
                invalid=1
            else:
                invalid=0

            file=StringIO(p)
            unpickler=Unpickler(file)
            # SDH: external references are reassembled elsewhere.
            # unpickler.persistent_load=self._persistent_load
            classification = unpickler.load()
            state = unpickler.load()

            # SDH: Let the object mapper do the state setting.
            # if hasattr(object, '__setstate__'):
            #     object.__setstate__(state)
            # else:
            #     d=object.__dict__
            #     for k,v in state.items(): d[k]=v
            osio = self._get_osio()
            event = osio.deserialize(oid, obj, classification, state)

            if event.upos:
                self._handle_unmanaged(obj, event.upos)

            self._set_serial(obj, serial)

            if invalid:
                if obj._p_independent():
                    try: del self._invalidated[oid]
                    except KeyError: pass
                else:
                    get_transaction().register(self)
                    raise ConflictError(object=obj)

        except ConflictError:
            raise
        except:
            LOG('ZODB',ERROR, "Couldn't load state for %s" % `oid`,
                error=sys.exc_info())
            raise


    def register(self, obj):
        """Register an object with the appropriate transaction manager.
        """
        assert obj._p_jar is self
        if obj._p_oid is not None:
            get_transaction().register(obj)
        # else someone is trying to trick ZODB into registering an
        # object with no OID.  OFS.Image.File._read_data() does this.
        # Since ApeConnection really needs meaningful OIDs, just ignore
        # the attempt.


    def __repr__(self):
        if self._version:
            ver = ' (in version %s)' % `self._version`
        else:
            ver = ''
        return '<%s at %08x%s>' % (self.__class__.__name__, id(self), ver)


    def _handle_unmanaged(self, obj, unmanaged):
        # Add an event handler to unmanaged subobjects.
        # The event handler calls self.register() when it changes.
        for o in unmanaged:
            if hasattr(o, '_p_oid'):  # Looks like a persistent object
                if o._p_jar is None:
                    o._p_oid = 'unmanaged'
                    o._p_jar = UnmanagedJar(self, obj._p_oid, o)
                else:
                    assert o._p_oid == 'unmanaged'
                    if o._p_changed is not None:
                        o._p_jar.save_state(o)


    # IObjectDatabase implementation

    get = _persistent_load

    def identify(self, obj):
        try:
            oid = obj._p_oid
        except AttributeError:
            raise TypeError("%s does not subclass Persistent" % repr(obj))
        if oid is None:
            return None
        if obj._p_jar is not self:
            raise InvalidObjectReference, (
                "Can't refer to %s, located in %s, from %s"
                % (repr(obj), repr(obj._p_jar), repr(self)))
        return oid

    def new_oid(self):
        return self._storage.new_oid()


    def get_class(self, module, name):
        return self._db._classFactory(self, module, name)


    def check_serials(self):
        """Verifies that all cached objects are in sync with the data.

        This is useful for finding gateways that generate inconsistent
        hashes.
        """
        for oid, ob in self._cache.items():
            if ob._p_changed is not None:
                self.before_load()
                p, serial = self._storage.load(oid, self._version)
                if serial != self._get_serial(ob):
                    raise StorageError(
                        "Inconsistent serial for oid %s" % repr(oid))
    
    def before_load(self):
        """Add self to the transaction before loading objects.

        This causes databases to be notified when the transaction
        completes.
        """
        if self._storage is None:
            text = ("Shouldn't load state for %s "
                   "when the connection is closed" % `oid`)
            LOG('ZODB', ERROR, text)
            raise RuntimeError(text)
        if not self.loaded_objects:
            self.loaded_objects = True
            get_transaction().register(self)
        
    def tpc_abort(self, transaction):
        self.loaded_objects = False
        Connection.tpc_abort(self, transaction)

    def tpc_finish(self, transaction):
        self.loaded_objects = False
        Connection.tpc_finish(self, transaction)

    def exportFile(self, oid, file=None):
        raise NotImplementedError('ZEXP Export not implemented')

    def importFile(self, file, clue='', customImporters=None):
        raise NotImplementedError('ZEXP Import not implemented')


    # A note on serials: Serials need to be stored independently of
    # objects because the current Persistent base class uses _p_serial
    # to derive _p_mtime.  Applications like Zope use _p_mtime, but
    # the _p_serial for Ape isn't always a date, so Ape can't use
    # _p_serial to store serials.  Instead, ApeConnection puts them in
    # a _serials dictionary.

    _serials = None
    serial_cleanup_threshold = 1000

    def _get_serial(self, ob):
        oid = ob._p_oid
        if oid is None or self._cache.get(oid, None) is not ob:
            return HASH0
        serials = self._serials
        if serials is None:
            return HASH0
        return serials.get(oid, HASH0)

    def _set_serial(self, ob, s):
        oid = ob._p_oid
        assert oid is not None
        if s is None:
            s = HASH0
        serials = self._serials
        if serials is None:
            serials = {}
            self._serials = serials
        if not serials.has_key(oid):
            # When the number of recorded serials exceeds the number of
            # cache entries by serial_cleanup_threshold, prune the serials
            # dictionary.
            if (len(serials) >= len(self._cache) +
                self.serial_cleanup_threshold):
                # clean up
                cache_get = self._cache.get
                for oid in serials.keys():
                    ob = cache_get(oid, None)
                    if ob is None or ob._p_changed is None:
                        del serials[oid]
        serials[oid] = s

    def _handle_serial(self, store_return, oid=None, change=1):
        """Handle the returns from store() and tpc_vote() calls."""

        # These calls can return different types depending on whether
        # ZEO is used.  ZEO uses asynchronous returns that may be
        # returned in batches by the ClientStorage.  ZEO1 can also
        # return an exception object and expect that the Connection
        # will raise the exception.

        # When commit_sub() exceutes a store, there is no need to
        # update the _p_changed flag, because the subtransaction
        # tpc_vote() calls already did this.  The change=1 argument
        # exists to allow commit_sub() to avoid setting the flag
        # again.
        if not store_return:
            return
        if isinstance(store_return, StringType):
            assert oid is not None
            serial = store_return
            obj = self._cache.get(oid, None)
            if obj is None:
                return
            if serial == ResolvedSerial:
                del obj._p_changed
            else:
                if change:
                    obj._p_changed = 0
                #obj._p_serial = serial
                self._set_serial(obj, serial)
        else:
            for oid, serial in store_return:
                if not isinstance(serial, StringType):
                    raise serial
                obj = self._cache.get(oid, None)
                if obj is None:
                    continue
                if serial == ResolvedSerial:
                    del obj._p_changed
                else:
                    if change:
                        obj._p_changed = 0
                    #obj._p_serial = serial
                    self._set_serial(obj, serial)



class UnmanagedJar:
    """Special jar for unmanaged persistent objects.

    There is one such jar for each unmanaged persistent object.  All
    it does is notify the managed persistent object of changes.

    Some applications ghostify unmanaged persistent objects.  To
    restore the state after ghostification, this jar keeps a reference
    to the state and restores it in setstate().  Note that when the
    managed persistent object that holds the unmanaged object gets
    ghosted, it usually removes the last reference to the unmanaged
    object, which is then deallocated.
    """

    def __init__(self, real_jar, real_oid, obj):
        self.real_jar = real_jar
        self.real_oid = real_oid
        self.save_state(obj)

    def save_state(self, obj):
        s = obj.__getstate__()
        if isinstance(s, DictType):
            s = s.copy()
        self.state = s

    def register(self, obj):
        o = self.real_jar[self.real_oid]
        if o._p_changed is None:
            # The application held on to this UPO even after its
            # container was ghosted.  The container needs to be
            # reactivated, but reactivation would create a new UPO in
            # place of the UPO held by this jar.  The application
            # would continue to refer to this old UPO.  Don't let the
            # application continue to change this abandoned object,
            # since all changes will be lost.
            raise StorageError(
                'Tried to change an unmanaged persistent object '
                'when the containing persistent object is a ghost')
        o._p_changed = 1

    def setstate(self, obj):
        obj.__setstate__(self.state)

    def modifiedInVersion(self, oid):
        # XXX PersistentExtra wants this
        return ''

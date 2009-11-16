import random, types, warnings

import ZODB.interfaces
import ZODB.POSException
import ZEO.Exceptions
import transaction
import transaction.interfaces
import persistent
import persistent.interfaces

import twisted.internet.defer
import twisted.internet.reactor
import twisted.python.failure

import zope.component
import zope.interface

import zc.twist._methodwrapper

METHOD_WRAPPER_TYPE = type({}.__setitem__)

def get_self(wrapper):
    if not isinstance(wrapper, METHOD_WRAPPER_TYPE):
        raise TypeError('unsupported type') # includes dict.__getitem__ :-/
    return zc.twist._methodwrapper._get_self(wrapper)

EXPLOSIVE_ERRORS = [SystemExit, KeyboardInterrupt,
                    ZODB.POSException.POSError]

# this is currently internal, though maybe we'll expose it later
class IDeferredReference(zope.interface.Interface):
    def __call__(self, connection):
        """return the actual object to be used."""

    db = zope.interface.Attribute("""
        The associated database, or None""")

class DeferredReferenceToPersistent(object):
    zope.interface.implements(IDeferredReference)

    name = None

    def __init__(self, obj):
        if isinstance(obj, types.MethodType):
            self.name = obj.__name__
            obj = obj.im_self
        elif isinstance(obj, METHOD_WRAPPER_TYPE):
            self.name = obj.__name__
            obj = get_self(obj)
        conn = ZODB.interfaces.IConnection(obj)
        self.db = conn.db()
        self.id = obj._p_oid

    def __call__(self, conn):
        if conn.db().database_name != self.db.database_name:
            conn = conn.get_connection(self.db.database_name)
        obj = conn.get(self.id)
        if self.name is not None:
            obj = getattr(obj, self.name)
        return obj

def Reference(obj):
    if isinstance(obj, types.MethodType):
        if (persistent.interfaces.IPersistent.providedBy(obj.im_self) and
            obj.im_self._p_jar is not None):
            return DeferredReferenceToPersistent(obj)
        else:
            return obj
    if isinstance(obj, METHOD_WRAPPER_TYPE):
        obj_self = get_self(obj)
        if (persistent.interfaces.IPersistent.providedBy(obj_self) and
            obj_self._p_jar is not None):
            return DeferredReferenceToPersistent(obj)
        else:
            return obj
    if (persistent.interfaces.IPersistent.providedBy(obj)
        and obj._p_jar is not None):
        return DeferredReferenceToPersistent(obj)
    return obj

def availableConnectionCount(db):
    try:                    # ZODB 3.9 and newer
        pool = db.pool
    except AttributeError:  # ZODB 3.8 and older
        pools = db._pools
        pool = pools.get('')    # version = ''
        if pool is None:
            return True
    size = db.getPoolSize()
    all = len(pool.all)
    available = len(pool.available) + (size - all)
    return available

missing = object()

def get_connection(db, deferred=None, backoff=0, reactor=None):
    if deferred is None:
        deferred = twisted.internet.defer.Deferred()
    backoff += random.random() / 20.0 + .0625 # 1/16 second (USE POWERS OF 2!)
    # if this is taking too long (i.e., the cumulative backoff is taking
    # more than half a second) then we'll just take one.  This might be
    # a bad idea: we'll have to see in practice.  Otherwise, if the
    # backoff isn't too long and we don't have a connection within our
    # limit, try again later.
    if backoff < .5 and not availableConnectionCount(db):
        if reactor is None:
            reactor = twisted.internet.reactor
        reactor.callLater(
            backoff, get_connection, db, deferred, backoff, reactor)
        return deferred
    deferred.callback(db.open(
        transaction_manager=transaction.TransactionManager()))
    return deferred

def truncate(str):
    if len(str) > 21: # 64 bit int or so
        str = str[:21]+"[...]"
    return str

class Failure(twisted.python.failure.Failure):

    sanitized = False

    def __init__(self, exc_value=None, exc_type=None, exc_tb=None):
        twisted.python.failure.Failure.__init__(
            self, exc_value, exc_type, exc_tb)
        self.__dict__ = twisted.python.failure.Failure.__getstate__(self)

    def cleanFailure(self):
        pass # already done

    def __getstate__(self):
        res = self.__dict__.copy()
        if not self.sanitized:
            res['stack'] = []
            res['frames'] = [
                [
                    v[0], v[1], v[2],
                    [(j[0], truncate(j[1])) for j in v[3]],
                    [] # [(j[0], truncate(j[1])) for j in v[4]]
                ] for v in self.frames
            ]

            res['sanitized'] = True
        return res

    def printTraceback(
        self, file=None, elideFrameworkCode=0, detail='default'):
        return twisted.python.failure.Failure.printTraceback(
            self, file, elideFrameworkCode or self.sanitized, detail)

class _Dummy: # twisted.python.failure.Failure is an old-style class
    pass # so we use old-style hacks instead of __new__

def sanitize(failure):
    # failures may have some bad things in the traceback frames.  This
    # converts everything to strings
    if not isinstance(failure, Failure):
        res = _Dummy()
        res.__class__ = Failure
        res.__dict__ = failure.__getstate__()
    else:
        res = failure
    return res

class Partial(object):

    # for TransactionErrors, such as ConflictErrors
    transaction_error_count = 0
    max_transaction_errors = 5

    # for ClientDisconnected errors
    backoff = None
    initial_backoff = 5 # seconds
    backoff_increment = 5 # seconds
    max_backoff = 60 # seconds

    # more general values
    attempt_count = 0
    _reactor = None

    def __init__(self, call, *args, **kwargs):
        self.call = Reference(call)
        self.args = list(Reference(a) for a in args)
        self.kwargs = dict((k, Reference(v)) for k, v in kwargs.iteritems())

    def __call__(self, *args, **kwargs):
        self.args.extend(args)
        self.kwargs.update(kwargs)
        db = None
        for src in ((self.call,), self.args, self.kwargs.itervalues()):
            for item in src:
                if IDeferredReference.providedBy(item) and item.db is not None:
                    db = item.db
                    break
            else:
                continue
            break
        else: # no persistent bits
            call, args, kwargs = self._resolve(None)
            return call(*args, **kwargs)
        d = twisted.internet.defer.Deferred()
        get_connection(db, reactor=self.getReactor()).addCallback(
            self._call, d)
        return d

    def setReactor(self, value):
        self._reactor = value
        return self

    def getReactor(self):
        if self._reactor is None:
            return twisted.internet.reactor
        return self._reactor

    def _resolve(self, conn):
        if IDeferredReference.providedBy(self.call):
            call = self.call(conn)
        else:
            call = self.call
        args = []
        for a in self.args:
            if IDeferredReference.providedBy(a):
                a = a(conn)
            args.append(a)
        kwargs = {}
        for k, v in self.kwargs.items():
            if IDeferredReference.providedBy(v):
                v = v(conn)
            kwargs[k] = v
        return call, args, kwargs

    def _call(self, conn, d):
        self.attempt_count += 1
        tm = transaction.interfaces.ITransactionManager(conn)
        try:
            tm.begin() # syncs; inside try:except because of ClientDisconnected
            call, args, kwargs = self._resolve(conn)
            res = call(*args, **kwargs)
            tm.commit()
        except ZODB.POSException.TransactionError:
            self.transaction_error_count += 1
            tm.abort()
            db = conn.db()
            conn.close()
            if (self.max_transaction_errors is not None and
                self.transaction_error_count >= self.max_transaction_errors):
                res = Failure()
                d.errback(res)
            else:
                get_connection(db, reactor=self.getReactor()).addCallback(
                    self._call, d)
        except ZEO.Exceptions.ClientDisconnected:
            tm.abort()
            db = conn.db()
            conn.close()
            if self.backoff is None:
                backoff = self.backoff = self.initial_backoff
            else:
                backoff = self.backoff = min(
                    self.backoff + self.backoff_increment, self.max_backoff)
            reactor = self.getReactor()
            reactor.callLater(
                backoff,
                lambda: get_connection(db, reactor=reactor).addCallback(
                    self._call, d))
        except EXPLOSIVE_ERRORS:
            tm.abort()
            conn.close()
            res = Failure()
            d.errback(res)
            raise
        except:
            tm.abort()
            conn.close()
            res = Failure()
            d.errback(res)
        else:
            conn.close()
            if isinstance(res, twisted.python.failure.Failure):
                d.errback(sanitize(res))
            elif isinstance(res, twisted.internet.defer.Deferred):
                res.chainDeferred(d)
            else: # the caller must not return any persistent objects!
                d.callback(res)

# also register this for adapting from IConnection
@zope.component.adapter(persistent.interfaces.IPersistent)
@zope.interface.implementer(transaction.interfaces.ITransactionManager)
def transactionManager(obj):
    conn = ZODB.interfaces.IConnection(obj) # typically this will be
    # zope.app.keyreference.persistent.connectionOfPersistent
    try:
        return conn.transaction_manager
    except AttributeError:
        return conn._txn_mgr
        # or else we give up; who knows.  transaction_manager is the more
        # recent spelling.

# very slightly modified from
# zope.app.keyreference.persistent.connectionOfPersistent; included to
# reduce dependencies
@zope.component.adapter(persistent.interfaces.IPersistent)
@zope.interface.implementer(ZODB.interfaces.IConnection)
def connection(ob):
    """An adapter which gets a ZODB connection of a persistent object.

    We are assuming the object has a parent if it has been created in
    this transaction.

    Returns None if it is impossible to get a connection.
    """
    cur = ob
    while getattr(cur, '_p_jar', None) is None:
        cur = getattr(cur, '__parent__', None)
        if cur is None:
            return None
    return cur._p_jar

# The Twisted Failure __getstate__, which we use in our sanitize function
# arguably out of paranoia, does a repr of globals and locals.  If the repr
# raises an error, they handle it gracefully.  However, if the repr has side
# effects, they can't know.  xmlrpclib unfortunately has this problem as of
# this writing.  This is a monkey patch to turn off this behavior, graciously
# provided by Florent Guillaume of Nuxeo.
# XXX see if this can be submitted somewhere as a bug/patch for xmlrpclib
import xmlrpclib
def xmlrpc_method_repr(self):
    return '<xmlrpc._Method %s>' % self._Method__name
xmlrpclib._Method.__repr__ = xmlrpc_method_repr
del xmlrpclib

===================================================
Twist: Talking to the ZODB in Twisted Reactor Calls
===================================================

The twist package contains a few functions and classes, but primarily a
helper for having a deferred call on a callable persistent object, or on
a method on a persistent object.  This lets you have a Twisted reactor
call or a Twisted deferred callback affect the ZODB.  Everything can be
done within the main thread, so it can be full-bore Twisted usage,
without threads.  There are a few important "gotchas": see the Gotchas_
section below for details.

The main API is `Partial`.  You can pass it a callable persistent object,
a method of a persistent object, or a normal non-persistent callable,
and any arguments or keyword arguments of the same sort.  DO NOT
use non-persistent data structures (such as lists) of persistent objects
with a database connection as arguments.  This is your responsibility.

If nothing is persistent, the partial will not bother to get a connection,
and will behave normally.

    >>> from zc.twist import Partial
    >>> def demo():
    ...     return 42
    ...
    >>> Partial(demo)()
    42

Now let's imagine a demo object that is persistent and part of a
database connection.  It has a `count` attribute that starts at 0, a
`__call__` method that increments count by an `amount` that defaults to
1, and an `decrement` method that reduces count by an `amount` that
defaults to 1 [#set_up]_.  Everything returns the current value of count.

    >>> demo.count
    0
    >>> demo()
    1
    >>> demo(2)
    3
    >>> demo.decrement()
    2
    >>> demo.decrement(2)
    0
    >>> import transaction
    >>> transaction.commit()

Now we can make some deferred calls with these examples.  We will use
`transaction.begin()` to sync our connection with what happened in the
deferred call.  Note that we need to have some adapters set up for this
to work.  The twist module includes implementations of them that we
will also assume have been installed [#adapters]_.

    >>> call = Partial(demo)
    >>> demo.count # hasn't been called yet
    0
    >>> deferred = call()
    >>> demo.count # we haven't synced yet
    0
    >>> t = transaction.begin() # sync the connection
    >>> demo.count # ah-ha!
    1

We can use the deferred returned from the call to do something with the
return value.  In this case, the deferred is already completed, so
adding a callback gets instant execution.

    >>> def show_value(res):
    ...     print res
    ...
    >>> ignore = deferred.addCallback(show_value)
    1

We can also pass the method.

    >>> call = Partial(demo.decrement)
    >>> deferred = call()
    >>> demo.count
    1
    >>> t = transaction.begin()
    >>> demo.count
    0

This also works for slot methods.

    >>> import BTrees
    >>> tree = root['tree'] = BTrees.family32.OO.BTree()
    >>> transaction.commit()
    >>> call = Partial(tree.__setitem__, 'foo', 'bar')
    >>> deferred = call()
    >>> len(tree)
    0
    >>> t = transaction.begin()
    >>> tree['foo']
    'bar'

Arguments are passed through.

    >>> call = Partial(demo)
    >>> deferred = call(2)
    >>> t = transaction.begin()
    >>> demo.count
    2
    >>> call = Partial(demo.decrement)
    >>> deferred = call(amount=2)
    >>> t = transaction.begin()
    >>> demo.count
    0

They can also be set during instantiation.

    >>> call = Partial(demo, 3)
    >>> deferred = call()
    >>> t = transaction.begin()
    >>> demo.count
    3
    >>> call = Partial(demo.decrement, amount=3)
    >>> deferred = call()
    >>> t = transaction.begin()
    >>> demo.count
    0

Arguments themselves can be persistent objects.  Let's assume a new demo2
object as well.

    >>> demo2.count
    0
    >>> def mass_increment(d1, d2, value=1):
    ...     d1(value)
    ...     d2(value)
    ...
    >>> call = Partial(mass_increment, demo, demo2, value=4)
    >>> deferred = call()
    >>> t = transaction.begin()
    >>> demo.count
    4
    >>> demo2.count
    4
    >>> demo.count = demo2.count = 0 # cleanup
    >>> transaction.commit()

ConflictErrors make it retry.

In order to have a chance to simulate a ConflictError, this time imagine
we have a runner that can switch execution from the call to our code
using `pause`, `retry` and `resume` (this is just for tests--remember,
calls used in non-threaded Twisted should be non-blocking!)
[#conflict_error_setup]_.

    >>> import sys
    >>> demo.count
    0
    >>> call = Partial(demo)
    >>> runner = Runner(call) # it starts paused in the middle of an attempt
    >>> call.attempt_count
    1
    >>> demo.count = 5 # now we will make a conflicting transaction...
    >>> transaction.commit()
    >>> runner.retry()
    >>> call.attempt_count # so it has to retry
    2
    >>> t = transaction.begin()
    >>> demo.count # our value hasn't changed...
    5
    >>> runner.resume() # but now call will be successful on the second attempt
    >>> call.attempt_count
    2
    >>> t = transaction.begin()
    >>> demo.count
    6

By default, after five ConflictError retries, the partial fails, raising the
last ConflictError.  This is returned to the deferred.  The failure put
on the deferred will have a sanitized traceback.  Here, imagine we have
a deferred (named `deferred`) created from such a an event
[#conflict_error_failure]_.

    >>> res = None
    >>> def get_result(r):
    ...     global res
    ...     res = r # we return None to quiet Twisted down on the command line
    ...
    >>> d = deferred.addErrback(get_result)
    >>> print res.getTraceback() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ZODB.POSException.ConflictError: database conflict error...

You can control how many ConflictError (and other transaction error) retries
should be performed by setting the ``max_transaction_errors`` attribute
[#max_transaction_errors]_.

ZEO ClientDisconnected errors are always retried, with a backoff that, by
default begins at 5 seconds and is never greater than 60 seconds
[#relies_on_twisted_reactor]_ [#use_original_demo]_ [#client_disconnected]_.

Other errors are returned to the deferred, like a transaction error that has
exceeded its available retries, as sanitized failures.

    >>> call = Partial(demo)
    >>> d = call('I do not add well with integers')
    >>> d = d.addErrback(get_result)
    >>> print res.getTraceback() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ...TypeError: unsupported operand type(s) for +=: 'int' and 'str'

The failure is sanitized in that the traceback is gone and the frame values
are turned in to reprs.  If you pickle the failure then it truncates the
reprs to a maximum of 20 characters plus "[...]" to indicate the
truncation [#show_sanitation]_.

The call tries to be a good connection citizen, waiting for a connection
if the pool is at its maximum size.  This code relies on the twisted
reactor; we'll use a `time_flies` function, which takes seconds to move
ahead, to simulate time passing in the reactor.

    >>> db.setPoolSize(1)
    >>> db.getPoolSize()
    1
    >>> demo.count = 0
    >>> transaction.commit()
    >>> call = Partial(demo)
    >>> res = None
    >>> deferred = call()
    >>> d = deferred.addCallback(get_result)
    >>> call.attempt_count
    0
    >>> time_flies(.1) >= 1 # returns number of connection attempts
    True
    >>> call.attempt_count
    0
    >>> res # None
    >>> db.setPoolSize(2)
    >>> db.getPoolSize()
    2
    >>> time_flies(.2) >= 1
    True
    >>> call.attempt_count > 0
    True
    >>> res
    1
    >>> t = transaction.begin()
    >>> demo.count
    1

If it takes more than a second or two, it will eventually just decide to grab
one.  This behavior may change.

    >>> db.setPoolSize(1)
    >>> db.getPoolSize()
    1
    >>> call = Partial(demo)
    >>> res = None
    >>> deferred = call()
    >>> d = deferred.addCallback(get_result)
    >>> call.attempt_count
    0
    >>> time_flies(.1) >= 1
    True
    >>> call.attempt_count
    0
    >>> res # None
    >>> time_flies(2.0) >= 2 # for a total of at least 3
    True
    >>> res
    2
    >>> t = transaction.begin()
    >>> demo.count
    2

Without a running reactor, this functionality will not work
[#teardown_monkeypatch]_.  Also, it relies on an undocumented, protected
attribute on the ZODB.DB, so is fragile across ZODB versions.

You can also specify a reactor for the partial using ``setReactor``, if
you don't want to use the standard one installed by twisted in
``twisted.internet.reactor``. [#setReactor]_

Gotchas
-------

For a certain class of jobs, you won't have to think much about using
the twist Partial.  For instance, if you are putting a result gathered by
work done by deferreds into the ZODB, and that's it, everything should be
pretty simple.  However, unfortunately, you have to think a bit harder for
other common use cases.

* As already mentioned, do not use arguments that are non-persistent
  collections (or even persistent objects without a connection) that hold
  any persistent objects with connections.

* Using persistent objects with connections but that have not been
  committed to the database will cause problems when used (as callable
  or argument), perhaps intermittently (if a commit happens before the
  partial is called, it will work).  Don't do this.

* Do not return values that are persistent objects tied to a connection.

* If you plan on firing off another reactor call on the basis of your
  work in the callable, realize that the work hasn't really "happened"
  until you commit the transaction.  The partial typically handles commits
  for you, committing if you return any result and aborting if you raise
  an error. But if you want to send off a reactor call on the basis of a
  successful transaction, you'll want to (a) do the work, then (b)
  commit, then (c) send off the reactor call.  If the commit fails,
  you'll get the standard abort and retry.

* If you want to handle your own transactions, do not use the thread
  transaction manager that you get from importing transaction.  This
  will cause intermittent, hard-to-debug, unexpected problems.  Instead,
  adapt any persistent object you get to
  transaction.interfaces.ITransactionManager, and use that manager for
  commits and aborts.

=========
Footnotes
=========

.. [#set_up] We'll actually create the state that the text describes here.

    >>> import persistent
    >>> class Demo(persistent.Persistent):
    ...     count = 0
    ...     def __call__(self, amount=1):
    ...         self._p_deactivate() # to be able to trigger ClientDisconnected
    ...         self.count += amount
    ...         return self.count
    ...     def decrement(self, amount=1):
    ...         self.count -= amount
    ...         return self.count
    ...
    >>> from ZODB.tests.util import DB
    >>> db = DB()
    >>> conn = db.open()
    >>> root = conn.root()
    >>> demo = root['demo'] = Demo()
    >>> demo2 = root['demo2'] = Demo()
    >>> import transaction
    >>> transaction.commit()

.. [#adapters] You must have two adapter registrations: IConnection to
    ITransactionManager, and IPersistent to IConnection.  We will also
    register IPersistent to ITransactionManager because the adapter is
    designed for it.

    >>> from zc.twist import transactionManager, connection
    >>> import zope.component
    >>> zope.component.provideAdapter(transactionManager)
    >>> zope.component.provideAdapter(connection)
    >>> import ZODB.interfaces
    >>> zope.component.provideAdapter(
    ...     transactionManager, adapts=(ZODB.interfaces.IConnection,))

    This quickly tests the adapters:

    >>> ZODB.interfaces.IConnection(demo) is conn
    True
    >>> import transaction.interfaces
    >>> transaction.interfaces.ITransactionManager(demo) is transaction.manager
    True
    >>> transaction.interfaces.ITransactionManager(conn) is transaction.manager
    True

.. [#conflict_error_setup] We also use this runner in the footnote below.

    >>> import threading
    >>> _main = threading.Lock()
    >>> _thread = threading.Lock()
    >>> class AltDemo(persistent.Persistent):
    ...     count = 0
    ...     def __call__(self, amount=1):
    ...         self.count += amount
    ...         assert _main.locked()
    ...         _main.release()
    ...         _thread.acquire()
    ...         return self.count
    ...
    >>> demo = root['altdemo'] = AltDemo()
    >>> transaction.commit()
    >>> class Runner(object):
    ...     def __init__(self, call):
    ...         self.call = call
    ...         self.thread = threading.Thread(target=self.run)
    ...         _thread.acquire()
    ...         _main.acquire()
    ...         self.thread.start()
    ...         _main.acquire()
    ...     def run(self):
    ...         self.running = True
    ...         self.result = self.call()
    ...         assert _main.locked()
    ...         assert _thread.locked()
    ...         _thread.release()
    ...         self.running = False
    ...         _main.release()
    ...     def retry(self):
    ...         assert _thread.locked()
    ...         _thread.release()
    ...         _main.acquire()
    ...     def resume(self):
    ...         while self.running:
    ...             self.retry()
    ...         self.thread.join()
    ...         assert not _thread.locked()
    ...         assert _main.locked()
    ...         _main.release()

.. [#conflict_error_failure] Here we create five consecutive conflict errors,
    which causes the call to give up.

    >>> call = Partial(demo)
    >>> runner = Runner(call)
    >>> for i in range(5):
    ...     demo.count = i
    ...     transaction.commit() # creates a write conflict
    ...     runner.retry()
    ...
    >>> demo.count
    4

    When we resume without a conflict error, it is too late: the result is a
    ConflictError.  The ConflictError is actually shown in the main text.

    >>> runner.resume()
    >>> demo.count
    4
    >>> call.attempt_count
    5
    >>> deferred = runner.result

.. [#max_transaction_errors] As the main text mentions, the
   ``max_transaction_errors`` attribute lets you set how many conflict errors
   should be retried.

    >>> call = Partial(demo)
    >>> call.max_transaction_errors
    5
    >>> call.max_transaction_errors = 10
    >>> call.max_transaction_errors
    10
    >>> runner = Runner(call)
    >>> for i in range(10):
    ...     demo.count = i
    ...     transaction.commit()
    ...     runner.retry()
    ...

   When we resume without a conflict error, it is too late: the result is a
   ConflictError.

    >>> runner.resume()
    >>> demo.count
    9
    >>> call.attempt_count
    10
    >>> deferred = runner.result

    >>> res = None
    >>> def get_result(r):
    ...     global res
    ...     res = r # we return None to quiet Twisted down on the command line
    ...
    >>> d = deferred.addErrback(get_result)
    >>> print res.getTraceback() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ZODB.POSException.ConflictError: database conflict error...

   Setting ``None`` means to retry conflict errors forever.  For our example,
   we will arbitrarily choose 50 iterations to show "forever".

    >>> call = Partial(demo)
    >>> call.max_transaction_errors
    5
    >>> call.max_transaction_errors = None
    >>> print call.max_transaction_errors
    None
    >>> runner = Runner(call)
    >>> for i in range(50):
    ...     demo.count = i
    ...     transaction.commit()
    ...     runner.retry()
    ...

   Now when we resume without a conflict error, we get a successful result: it
   never gave up.

    >>> runner.resume()
    >>> runner.result # doctest: +ELLIPSIS
    <Deferred at ...  current result: 50>
    >>> _ = transaction.begin() # we need to sync to get changes
    >>> demo.count # notice, 49 + 1
    50

.. [#relies_on_twisted_reactor] We monkeypatch twisted.internet.reactor
    (and revert it in another footnote below).

    >>> import twisted.internet.reactor
    >>> oldCallLater = twisted.internet.reactor.callLater
    >>> import bisect
    >>> class FauxReactor(object):
    ...     def __init__(self):
    ...         self.time = 0
    ...         self.calls = []
    ...     def callLater(self, delay, callable, *args, **kw):
    ...         res = (delay + self.time, callable, args, kw)
    ...         bisect.insort(self.calls, res)
    ...         # normally we're supposed to return something but not needed
    ...     def time_flies(self, time):
    ...         end = self.time + time
    ...         ct = 0
    ...         while self.calls and self.calls[0][0] <= end:
    ...             self.time, callable, args, kw = self.calls.pop(0)
    ...             callable(*args, **kw) # normally this would get try...except
    ...             ct += 1
    ...         self.time = end
    ...         return ct
    ...
    >>> faux = FauxReactor()
    >>> twisted.internet.reactor.callLater = faux.callLater
    >>> time_flies = faux.time_flies

.. [#use_original_demo] The second demo has too much thread code in it:
    we'll use the old demo for the rest of the discussion.

    >>> demo = root['demo']

.. [#client_disconnected] As the main text describes,
   ZEO.Exceptions.ClientDisconnected errors will always be retried, but with a
   backoff.

   First we'll mimic a disconnected ZEO at the start of a transaction.

    >>> from ZEO.Exceptions import ClientDisconnected
    >>> raise_error = [1]
    >>> storage_class = db._storage.__class__
    >>> original_load = storage_class.load
    >>> def load(self, oid, version):
    ...     if raise_error:
    ...         raise_error.pop()
    ...         raise ClientDisconnected()
    ...     else:
    ...         return original_load(self, oid, version)
    ...
    >>> _ = transaction.begin()
    >>> demo.count
    0
    >>> call = Partial(demo)
    >>> storage_class.load = load

   We rely on a reactor to implement delayed calls.  We have a fake reactor
   called ``faux`` for these examples.  It has a list of pending calls, and
   we can call ``time_flies`` to make time appear to pass.

    >>> len(faux.calls)
    0

   When we first call the partial, it will fail, and reschedule for later.

    >>> len(faux.calls)
    0
    >>> deferred = call()
    >>> deferred.called
    0
    >>> len(faux.calls)
    1

   The rescheduling is initially for five seconds later, by default.  In this
   first example, after the first retry, the call will succeed.

    >>> faux.calls[0][0] - faux.time
    5
    >>> time_flies(1) # 1 second
    0
    >>> deferred.called
    0
    >>> time_flies(1) # 1 second
    0
    >>> deferred.called
    0
    >>> time_flies(1) # 1 second
    0
    >>> deferred.called
    0
    >>> time_flies(1) # 1 second
    0
    >>> deferred.called
    0
    >>> time_flies(1) # 1 second
    1
    >>> deferred.called
    True
    >>> deferred.result
    1
    >>> len(faux.calls)
    0

   By default, the rescheduling backoff increases by five seconds for every
   retry, to a maximum of a 60 second backoff.

    >>> call = Partial(demo)
    >>> raise_error.extend([1] * 30)
    >>> len(faux.calls)
    0
    >>> deferred = call()
    >>> deferred.called
    0
    >>> len(faux.calls)
    1
    >>> def run(deferred):
    ...     sleeps = []
    ...     for i in range(31):
    ...         if deferred.called:
    ...             break
    ...         else:
    ...             sleep = faux.calls[0][0] - faux.time
    ...             sleeps.append(sleep)
    ...             time_flies(sleep)
    ...     else:
    ...         print 'oops'
    ...     return sleeps
    ...
    >>> sleeps = run(deferred)
    >>> deferred.result
    2
    >>> len(sleeps)
    30
    >>> sleeps # doctest: +ELLIPSIS
    [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 60, 60,..., 60, 60, 60, 60]

   The default backoff values can be changed by setting the instance attributes
   ``initial_backoff``, ``backoff_increment``, and ``max_backoff``.

    >>> call = Partial(demo)
    >>> call.initial_backoff
    5
    >>> call.backoff_increment
    5
    >>> call.max_backoff
    60
    >>> call.initial_backoff = 4
    >>> call.backoff_increment = 2
    >>> call.max_backoff = 21
    >>> raise_error.extend([1] * 30)
    >>> len(faux.calls)
    0
    >>> deferred = call()
    >>> deferred.called
    0
    >>> len(faux.calls)
    1
    >>> sleeps = run(deferred)
    >>> deferred.result
    3
    >>> len(sleeps)
    30
    >>> sleeps # doctest: +ELLIPSIS
    [4, 6, 8, 10, 12, 14, 16, 18, 20, 21, 21, 21, 21, 21, 21,..., 21, 21, 21]

   A ClientDisconnected error can also occur during transaction commit.

    >>> storage_class.load = original_load

    >>> from transaction import TransactionManager
    >>> old_commit = TransactionManager.commit
    >>> commit_count = 0
    >>> error = None
    >>> max = 2
    >>> raise_error = [1] # change state to active
    >>> def new_commit(self):
    ...     if raise_error:
    ...         raise_error.pop()
    ...         raise ClientDisconnected()
    ...     else:
    ...         old_commit(self) # changing state to "active" or similar
    ...
    >>> TransactionManager.commit = new_commit
    >>> call = Partial(demo)
    >>> len(faux.calls)
    0
    >>> deferred = call()
    >>> deferred.called
    0
    >>> len(faux.calls)
    1

    >>> faux.calls[0][0] - faux.time
    5
    >>> time_flies(4) # 4 seconds
    0
    >>> deferred.called
    0
    >>> time_flies(1) # 1 second
    1
    >>> deferred.called
    True
    >>> deferred.result
    4
    >>> len(faux.calls)
    0

    >>> TransactionManager.commit = old_commit
    >>> _ = transaction.begin()

.. [#show_sanitation] Before pickling, the failure includes full information
    about before and after the exception was caught, as well as locals and
    globals.  Everything has been repr'd, though, and the traceback object
    removed.

    >>> print res.getTraceback() # doctest: +ELLIPSIS
    Traceback (most recent call last):
      File ".../zc/twist/__init__.py", line ..., in __call__
        get_connection(db, reactor=self.getReactor()).addCallback(
      File ".../twisted/internet/defer.py", line ..., in addCallback...
    --- <exception caught here> ---
      File ".../zc/twist/__init__.py", line ..., in _call
        res = call(*args, **kwargs)
      File "<doctest README.txt[...]>", line ..., in __call__
        self.count += amount
    exceptions.TypeError: unsupported operand type(s) for +=: 'int' and 'str'
    <BLANKLINE>

    (The failure traceback at "verbose" detail is wildly verbose--this example
    takes out more than 90% of the text, just so you know.)

    >>> print res.getTraceback(detail='verbose') # doctest: +ELLIPSIS
    *--- Failure #... (pickled) ---
    .../zc/twist/__init__.py:...: __call__(...)
     [ Locals ]...
      args : "('I do not add well with integers',)...
     ( Globals )...
      Partial : "<class 'zc.twist.Partial'>...
    .../twisted/internet/defer.py:...: addCallback(...)
     [ Locals ]...
      args : '(<Deferred at ...
     ( Globals )...
      Deferred : '<class twisted.internet.defer.Deferred at ...
    --- <exception caught here> ---
    .../zc/twist/__init__.py:...: _call(...)
     [ Locals ]...
      args : "['I do not add well with integers']...
     ( Globals )...
      Partial : "<class 'zc.twist.Partial'>...
    <doctest README.txt[...]>:...: __call__(...)
     [ Locals ]...
      amount : "'I do not add well with integers'...
     ( Globals )...
      Partial : "<class 'zc.twist.Partial'>...
    exceptions.TypeError: unsupported operand type(s) for +=: 'int' and 'str'
    *--- End of Failure #... ---
    <BLANKLINE>

    After pickling, the failure only includes information for when the
    exception was caught and beyond (after the "--- <exception caught
    here> ---" lines above), does not have globals, and has local reprs
    truncated to a maximum of 20 characters plus "[...]" to indicate the
    truncation. This addresses past problems of large pickle size for
    failures, which can cause performance problems.

    >>> import pickle
    >>> print pickle.loads(pickle.dumps(res)).getTraceback()
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
      File ".../zc/twist/__init__.py", line ..., in _call
        res = call(*args, **kwargs)
      File "<doctest README.txt[...]>", line ..., in __call__
        self.count += amount
    exceptions.TypeError: unsupported operand type(s) for +=: 'int' and 'str'
    <BLANKLINE>

    >>> print pickle.loads(pickle.dumps(res)).getTraceback(detail='verbose')
    ... # doctest: +ELLIPSIS
    *--- Failure #... (pickled) ---
    .../src/zc/twist/__init__.py:...: _call(...)
     [ Locals...
      self : '<zc.twist.Partial obj[...]...
     ( Globals )
    <doctest README.txt[...]>:...: __call__(...)
     [ Locals...
      amount : "'I do not add well wi[...]...
     ( Globals )
    exceptions.TypeError: unsupported operand type(s) for +=: 'int' and 'str'
    *--- End of Failure #... ---
    <BLANKLINE>

.. [#teardown_monkeypatch]

    >>> twisted.internet.reactor.callLater = oldCallLater

.. [#setReactor]

    >>> db.setPoolSize(1)
    >>> db.getPoolSize()
    1
    >>> demo.count = 0
    >>> transaction.commit()
    >>> call = Partial(demo).setReactor(faux)
    >>> res = None
    >>> deferred = call()
    >>> d = deferred.addCallback(get_result)
    >>> call.attempt_count
    0
    >>> time_flies(.1) >= 1 # returns number of connection attempts
    True
    >>> call.attempt_count
    0
    >>> res # None
    >>> db.setPoolSize(2)
    >>> db.getPoolSize()
    2
    >>> time_flies(.2) >= 1
    True
    >>> call.attempt_count > 0
    True
    >>> res
    1
    >>> t = transaction.begin()
    >>> demo.count
    1

If it takes more than a second or two, it will eventually just decide to grab
one.  This behavior may change.

    >>> db.setPoolSize(1)
    >>> db.getPoolSize()
    1
    >>> call = Partial(demo).setReactor(faux)
    >>> res = None
    >>> deferred = call()
    >>> d = deferred.addCallback(get_result)
    >>> call.attempt_count
    0
    >>> time_flies(.1) >= 1
    True
    >>> call.attempt_count
    0
    >>> res # None
    >>> time_flies(1.9) >= 2 # for a total of at least 3
    True
    >>> res
    2
    >>> t = transaction.begin()
    >>> demo.count
    2

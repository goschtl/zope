
from persistent.interfaces import IPersistent

from zope import interface, schema
from zope.app.location.interfaces import ILocation
from zope.app.container.interfaces import IReadContainer

PENDING = 'PENDING'
ACTIVE = 'ACTIVE'
CALLBACK = 'CALLBACK'
COMPLETED = 'COMPLETED'

class IPerisistentDeferred(IPersistent):

    # TODO: MUST be annotatable.

    def addCallbacks(success=None, failure=None):
        """Add callbacks (success and/or failure) to this Deferred.

        These will be executed when this deferred's callback chain is run from
        `callback`.

        A callback may return a result, a twisted.python.failure,
        or an IPersistentDeferred; or it may raise an exception, which will be
        converted to a failure.  A callback of `None` is interpreted as a
        transparent callback that does no processing and forwards the value
        it got to the next link in the chain.

        If the deferred has already been called, the new success or failure
        callback, as appropriate from the last result, will be immediately
        called.

        Callbacks and their return values must be persistable.
        """
        # to chain deferred d2 to deferred d1, use
        # "d1.addCallbacks(d2.callBack, d2.callBack)"

    def callBack(result):
        """Begin this deferred's callbacks.  If the result is a
        failure.Failure, call the first failure callback, else call the first
        success callback.

        Each callback will have its result passed as the first
        argument to the next; this way, the callbacks act as a
        'processing chain'. Also, if the success-callback returns a Failure
        or raises an Exception, processing will continue on the *failure*
        callback chain.

        A deferred may only have `callBack` called once.  If the deferred
        is in the CALLBACK or COMPLETED state, an AlreadyCalledError will be
        raised.
        """

    def setExpiration(datetime):
        """if deferred has not been called by `datetime`, callBack a Failure.

        The twisted.python.failure.Failure will be of a
        zope.zasync.interfaces.TimeoutError.

        `datetime` must be from Python standard library datetime module. If
        the datetime is timezone-naive, it will be converted to a
        timezone-aware datetime with a pytz.FixedOffset timezone based on the
        current system's concept of local time.

        setExpiration can be called multiple times, but the new datetime can
        never be greater (later) than the current value.

        `d.setExpiration(datetime.datetime.now())` is a reasonable spelling
        for canceling a deferred.
        """
        # Note that a similar function (`setTimeout`) has been deprecated in
        # the Twisted deferred but is not deprecated in this interface. The
        # Twisted concern is that the setTimeout method in the Twisted
        # interface includes a method to be called on timeout, when in fact it
        # is the code that manages the deferred that should handle a timeout.
        # This interface bypasses the problem by not allowing a method to be
        # called. Code that manages a deferred and that wants or needs to
        # react to a timeout call should register an errback for it.


    def getExpiration():
        """Return the expiration value for the deferred, or None if not set"""

    result = Attribute(
        """The deferred's current effective result (or failure).  Readonly.

        This result is as processed by success and errorbacks, if any.

        Initializes to None. Because None is a possible valid result, this
        does not indicate the state of the deferred: use `state`.""")

    completed_callbacks = interface.Attribute(
        """Readonly tuple of information about the completed callbacks.

        Each element in the tuple is itself a tuple of (active callback data,
        alternate callback data, datetime added, datetime started, input
        value, datetime finished, output value), where the active callback
        data is a tuple of (callback, args, kwargs) and the alternate callback
        data is of the same structure or None.""")

    active_callback = interface.Attribute(
        """Information about the current active callback, or None.

        Only callbacks that return an IPersistentDeferred will be recorded
        here, as they wait for the deferred to be completed.

        The data is a tuple of (active callback data, alternate callback data,
        datetime added, datetime started, input value, callback deferred),
        where the active callback data is a tuple of (callback, args, kwargs)
        and the alternate callback data is of the same structure or None.""")

    pending_callbacks = interface.Attribute(
        """Readonly tuple of information about pending callbacks.

        Each element in the pending callbacks is itself a tuple of
        (success callback data, failure callback data, datetime added), where
        the callback data is either None or a tuple of (callback, args,
        kwargs).""")

    state = interface.Attribute(
        """One of the constants PENDING, ACTIVE, CALLBACK, and COMPLETED.

        Readonly.

        A pending task has not yet been
        """) # created, considered, started, taskcompleted,
        # callback completed (number remaining), callback added; use
        # objectlog and events!

    __parent__ = interface.Attribute(
        """The IAsynchronousTask that uses this deferred""")

class IAsynchronousTask(IPersistent, ILocation):
    """ILocation.__parent__ must be queue that contains the task"""

    def perform():
        """perform the task.

        May only be called once.  Use `retry` for retries.

        Usually will return a deferred, but might also return a result or
        failure directly, or raise an exception."""

    deferred = interface.Attribute(
        "The IPersistentDeferred associated with the task")

    def retry():
        """the task was stopped, and now has a chance to retry.

        Same contract as `perform` but different semantics."""

class IResourceAwareAsynchronousTask(IAsynchronousTask):

    per_process_resources = interface.Attribute(
        """Iterable of resources that the task needs within a worker process.

        Resources needed from a process are typically a thread, a thread with
        a database connection from a shared pool, and so on.  Strings and
        interfaces can be used to represent these resources in this attribute
        as a shared convention between workers and tasks. The values
        must be persistable.

        The zope.zasync.interfaces file includes the
        following interfaces to be used for this purpose:
        IAsynchronousWorkerThread, IAsynchronousWorkerZODBThread

        Adding a task to a task queue checks to make sure that a registered
        available worker provides all of the requested resources.
        """)

    per_database_resources = interface.Attribute(
        """Iterable of resources that the task needs across a database.

        Resources needed across a database are typically persistent objects
        that a task will want to write (to reduce the chance of conflict
        errors), but may also be specially requested resources represented
        with strings and interfaces. The values must be persistable.

        Adding a task to a task queue checks to make sure that the task
        queue can provide all of the requested resources.  The only default
        behavior for a task queue is to be able to handle any persistent
        object.
        """)

class IAsynchronousTaskQueue(IPersistent, IReadContainer):

    def add(task, holdUntil=None, worker_ids=None, force=False):
        """Add a new task, optionally held till after timezone-aware datetime.

        Sets tasks __parent__ to this queue, and assigns __name__. If task's
        deferred is in any state other than PENDING, raise ValueError.

        XXX specifying worker_ids says that only workers with ids in iterable
        may be used (specified worker ids may be globs--see fnmatch

        XXX throws exception if task requests resource that queue or
        registered workers do not provide, unless force is True, in which
        case it's logged and accepted.
        """

    def iterAvailable():
        """iter through tasks that are currently available to be performed.

        Items should typically be in order of creation date.
        """

    def iterHeld(worker=None):
        """iter through pairs of (datetime, task) for held pending tasks.

        If worker is provided, only lists tasks appropriate for that given
        worker."""

    def iterClaimed():
        """iter through pairs of (worker, task) for claimed tasks.
        """

    def resetClaimed(worker_id):
        """Reset claimed tasks for the worker_id to being available for retry.
        """

    def getWorkerStatus(worker_id=None):
        """Return the status for all or specified worker.

        Status is dictionary of keys `id`, `last_pong`, `poll_interval`,
        `hostname`, `pid`."""

    def registerWorker(worker):
        """Register a worker with queue.
        Should be called every time worker polls.  Responsible for replying to
        ping request.
        """

    def unregisterWorker(worker):
        """Unregister a worker from queue"""

    def ping(worker_id, expiration=None):
        """Request that worker of worker_id reply.

        Deferred is returned that will accept pong or expire.  expiration
        defaults to now + twice the last registered poll_interval for the
        worker, or a minute otherwise."""

    def cancelPending(task):
        """Cancel a pending task.

        Raises ValueError if task's deferred is not PENDING or task is not
        in the queue.
        """

    def claim(task, worker):
        """

        remembers worker id.

        records a pong from worker.
        """

    def callBack(task, worker, result):
        """release claim on task and return result.

        Record a pong from worker.
        """

    rotation_period = Attribute(
        """The rotation period in seconds for the resolved deferred cache
        """)

    unresolved = interface.Attribute(
        """A container of tasks that a worker is currently working on.

        May be working on main task (ACTIVE status) or on callbacks (CALLBACK
        status).
        """)

    resolved = interface.Attribute(
        """A container of tasks that are resolved (mail task and callbacks).

        Adding a new callback to a completed task should move it back to the
        unresolved container if the necessary subscriber is registered.

        Should rotate out resolved tasks.
        """)

class IAsynchronousWorker(interface.Interface):
    """Is, or represents, the worker."""

    # available_resources

    id = interface.Attribute(
        """the id of the worker.

        Suggested to be hostname + PID""")

    poll_interval = interface.Attribute(
        """The approximate period of polling for the zasync process.
        """)

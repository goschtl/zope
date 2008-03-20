============================
Configuration Without Zope 3
============================

This section discusses setting up zc.async without Zope 3.  Since Zope 3
is ill-defined, we will be more specific: this describes setting up
zc.async without ZCML, without any zope.app packages, and with as few
dependencies as possible.  A casual way of describing the dependencies
is "ZODB and zope.component"[#specific_dependencies]_.

The next section, `Configuration With Zope 3`_, still tries to limit
dependencies, but includes both ZCML and indirect and direct
dependencies on such packages as zope.publisher and zope.app.appsetup.

Configuration has three basic parts: component registrations, ZODB
setup, and ZODB configuration.

Component Registrations
=======================

Some registrations are required, and some are optional.  Since they are
component registrations, even for the required registrations, other
implementations are possible.

--------
Required
--------

You must have three adapter registrations: IConnection to
ITransactionManager, IPersistent to IConnection, and IPersistent to
ITransactionManager.

The ``zc.twist`` package provides all of these adapters.  However,
zope.app.keyreference also provides a version of the ``connection`` adapter
that is identical or very similar, and that should work fine if you are 
already using that package in your application.

    >>> from zc.twist import transactionManager, connection
    >>> import zope.component
    >>> zope.component.provideAdapter(transactionManager)
    >>> zope.component.provideAdapter(connection)
    >>> import ZODB.interfaces
    >>> zope.component.provideAdapter(
    ...     transactionManager, adapts=(ZODB.interfaces.IConnection,))

We also need to be able to adapt functions and methods to jobs.  The
zc.async.job.Job class is the expected implementation.

    >>> import types
    >>> import zc.async.interfaces
    >>> import zc.async.job
    >>> zope.component.provideAdapter(
    ...     zc.async.job.Job,
    ...     adapts=(types.FunctionType,),
    ...     provides=zc.async.interfaces.IJob)
    >>> zope.component.provideAdapter(
    ...     zc.async.job.Job,
    ...     adapts=(types.MethodType,),
    ...     provides=zc.async.interfaces.IJob)
    ...

--------
Optional
--------

UUID
----

The dispatcher will look for a UUID utility if a UUID is not specifically
provided to its constructor.
    
    >>> from zc.async.instanceuuid import UUID
    >>> zope.component.provideUtility(
    ...     UUID, zc.async.interfaces.IUUID, '')

The UUID we register here is a UUID of the instance, which is expected
to uniquely identify the process when in production. It is stored in
INSTANCE_HOME/etc/uuid.txt.

    >>> import uuid
    >>> import os
    >>> f = open(os.path.join(
    ...     os.environ.get("INSTANCE_HOME"), 'etc', 'uuid.txt'))
    >>> uuid_hex = f.readline().strip()
    >>> f.close()
    >>> uuid = uuid.UUID(uuid_hex)
    >>> UUID == uuid
    True

The uuid.txt file is intended to stay in the instance home as a
persistent identifier.

Queue Adapter
-------------

You may want to set up an adapter from persistent objects to a named queue.
The zc.async.queue.getDefaultQueue adapter is a reasonable approach.

    >>> import zc.async.queue
    >>> zope.component.provideAdapter(zc.async.queue.getDefaultQueue)

This returns the queue names '' (empty string).

Agent Subscribers
-----------------

As we'll see below, the dispatcher fires an event when it registers with
a queue, and another when it activates the queue.  These events give you
the opportunity to register subscribers to add one or more agents to a
queue, to tell the dispatcher what jobs to perform.
zc.async.agent.addMainAgentActivationHandler is a reasonable starter: it
adds a single agent named 'main' if one does not exist.  The agent has a
simple indiscriminate FIFO policy for the queue.  If you want to write
your own subscriber, look at this.

Agents are an important part of the ZODB configuration, and so are described
more in depth below.

    >>> import zc.async.agent
    >>> zope.component.provideHandler(
    ...     zc.async.agent.addMainAgentActivationHandler)

This subscriber is registered for the IDispatcherActivated event; another
approach might use the IDispatcherRegistered event.

Database Startup Subscribers
----------------------------

Typically you will want to start the reactor, if necessary, and instantiate
and activate the dispatcher when the database is ready.  Depending on your
application, this can be done in-line with your start up code, or with a
subscriber to some event.

Zope 3 provides an event, zope.app.appsetup.interfaces.IDatabaseOpenedEvent,
that the Zope 3 configuration uses.  You may also want to follow this kind
of pattern.

For our example, we will start the dispatcher in-line (see the beginning of
the `ZODB Configuration`_ section).

ZODB Setup
==========

--------------------
Storage and DB Setup
--------------------

On a basic level, zc.async needs a setup that supports good conflict
resolution.  Most or all production ZODB storages now have the necessary
APIs to support MVCC.  You should also make sure that your ZEO server
has all the code that includes conflict resolution, such as zc.queue.

A more subtle decision is whether to use multiple databases.  The zc.async
dispatcher can generate a lot of database churn.  It may be wise to put the
queue in a separate database from your content database(s).  

The downsides to this option include the fact that you must be careful to
specify to which database objects belong; and that broken cross-database
references are not handled gracefully in the ZODB as of this writing.

We will use multiple databases for our example here.  See the footnote in
the usage section that sets up the tests for a non-multiple database
approach.

(We use a FileStorage rather than a MappingStorage variant typical in
tests and examples because we want MVCC, as mentioned above.)

    >>> databases = {}
    >>> import ZODB.FileStorage
    >>> storage = ZODB.FileStorage.FileStorage(
    ...     'main.fs', create=True)
    
    >>> async_storage = ZODB.FileStorage.FileStorage(
    ...     'async.fs', create=True)

    >>> from ZODB.DB import DB 
    >>> databases[''] = db = DB(storage)
    >>> databases['async'] = async_db = DB(async_storage)
    >>> async_db.databases = db.databases = databases
    >>> db.database_name = ''
    >>> async_db.database_name = 'async'
    >>> conn = db.open()
    >>> root = conn.root()

---------
DB layout
---------

Dispatchers look for queues in a mapping off the root of the database in 
a key defined as a constant: zc.async.interfaces.KEY.  This mapping should
generally be a zc.async.queue.Queues object.

If we were not using a multi-database for our example, we could simply install
the queues mapping with this line:
``root[zc.async.interfaces.KEY] = zc.async.queue.Queues()``.  We will need
something a bit more baroque.  We will add the queues mapping to the 'async'
database, and then make it available in the main database ('') with the proper
key.

    >>> conn2 = conn.get_connection('async')
    >>> queues = conn2.root()['mounted_queues'] = zc.async.queue.Queues()

Note that the 'mounted_queues' key in the async database is arbitrary:
what we care about is the key in the database that the dispatcher will
see.

Now we add the object explicitly to conn2, so that the ZODB will know the
"real" database in which the object lives, even though it will be also
accessible from the main database.

    >>> conn2.add(queues)
    >>> root[zc.async.interfaces.KEY] = queues
    >>> import transaction
    >>> transaction.commit()

Now we need to put a queue in the queues collection.  We can have more than
one, as discussed below, but we suggest a convention of the primary queue
being available in a key of '' (empty string).

    >>> queue = queues[''] = zc.async.queue.Queue()
    >>> transaction.commit()

We can now get the queue with the optional adapter from IPersistent to IQueue
above.

    >>> queue is zc.async.interfaces.IQueue(root)
    True

ZODB Configuration
==================

Now we can start the reactor, and start the dispatcher.  As noted above,
in some applications this may be done with an event subscriber.  We will
do it inline.

Any object that conforms to the specification of zc.async.interfaces.IReactor
will be usable by the dispatcher.  For our example, we will use our own instance
of the Twisted select-based reactor running in a separate thread.  This is
separate from the Twisted reator installed in twisted.internet.reactor, and
so this approach can be used with an application that does not otherwise use
Twisted (for instance, a Zope application using the "classic" zope publisher).

The testing module also has a reactor on which the `Usage` section relies.

Configuring the basics is fairly simple, as we'll see in a moment.  The
trickiest part is to handle signals cleanly.  Here we install signal
handlers in the main thread using ``reactor._handleSignals``.  This may
work in some real-world applications, but if your application already
needs to handle signals you may need a more careful approach.  The Zope
3 configuration has some options you can explore.  

    >>> import twisted.internet.selectreactor
    >>> reactor = twisted.internet.selectreactor.SelectReactor()
    >>> reactor._handleSignals()

Now we are ready to instantiate our dispatcher.

    >>> dispatcher = zc.async.dispatcher.Dispatcher(db, reactor)

Notice it has the uuid defined in instanceuuid.

    >>> dispatcher.UUID == UUID
    True

Now we can start the reactor and the dispatcher in a thread.

    >>> import threading
    >>> def start():
    ...     dispatcher.activate()
    ...     reactor.run(installSignalHandlers=0)
    ...
    >>> thread = threading.Thread(target=start)
    >>> thread.setDaemon(True)

    >>> thread.start()

The dispatcher should be starting up now.  Let's wait for it to activate.
We're using a test convenience, get_poll, defined in the footnotes
[#get_poll]_.

    >>> poll = get_poll(0)

We're off!  The events have been fired for registering and activating the
dispatcher.  Therefore, our subscriber to add our agent has fired.

We need to begin our transaction to synchronize our view of the database.

    >>> t = transaction.begin()

We get the collection of dispatcher agents from the queue, using the UUID.

    >>> dispatcher_agents = queue.dispatchers[UUID]

It has one agent--the one placed by our subscriber.

    >>> dispatcher_agents.keys()
    ['main']
    >>> agent = dispatcher_agents['main']

Now we have our agent!  But...what is it[#stop_reactor]_?

------
Agents
------

Agents are the way you control what a dispatcher's worker threads do.  They
pick the jobs and assign them to their dispatcher when the dispatcher asks.

*If a dispatcher does not have any agents in a give queue, it will not perform
any tasks for that queue.*

We currently have an agent that simply asks for the next available FIFO job.
We are using an agent implementation that allows you to specify a callable to
choose the job.  That callable is now zc.async.agent.chooseFirst.

    >>> agent.chooser is zc.async.agent.chooseFirst
    True

Here's the entire implementation of that function::

    def chooseFirst(agent):
        return agent.queue.claim()

What would another agent do?  Well, it might pass a filter function to
``claim``.  This function takes a job and returns a value evaluated as a
boolean.  For instance, let's say we always wanted a certain number of
threads available for working on a particular call; for the purpose of
example, we'll use ``operator.mul``, though a more real-world example
might be a network call or a particular call in your application.

    >>> import operator
    >>> def chooseMul(agent):
    ...     return agent.queue.claim(lambda job: job.callable is operator.mul)
    ...

Another variant would prefer operator.mul, but if one is not in the queue,
it will take any.

    >>> def preferMul(agent):
    ...     res = agent.queue.claim(lambda job: job.callable is operator.mul)
    ...     if res is None:
    ...         res = agent.queue.claim()
    ...     return res
    ...

Other approaches might look at the current jobs in the agent, or the agent's
dispatcher, and decide what jobs to prefer on that basis.  The agent should
support many ideas.

Let's set up another agent, in addition to the ``chooseFirst`` one, that has
the ``preferMul`` policy.

    >>> agent2 = dispatcher_agents['mul'] = zc.async.agent.Agent(preferMul)

Another characteristic of agents is that they specify how many jobs they
should pick at a time.  The dispatcher actually adjusts the size of the
ZODB connection pool to accommodate its agents' size.  The default is 3.

    >>> agent.size
    3
    >>> agent2.size
    3

We'll manipulate that a little later.

Finally, it's worth noting that agents contain the jobs that are currently
be worked on by the dispatcher, on their behalf; and have a ``completed``
collection of the more recent completed jobs, beginnin with the most recently
completed job.

---------------
Multiple Queues
---------------

Since we put our queues in a mapping of them, we can also create multiple
queues.  This can make some scenarios more convenient and simpler to reason
about.  For instance, while you might have agents filtering jobs as we
describe above, it might be simpler to say that you have a queue for one kind
of job--say, processing a video file or an audio file--and a queue for other
kinds of jobs.  Then it is easy and obvious to set up simple FIFO agents
as desired for different dispatchers.  The same kind of logic could be
accomplished with agents, but it is easier to picture the multiple queues.

------
Quotas
------

We touched on quotas in the usage section.  Some jobs will need to
access resoources that are shared across processes.  A central data
structure such as an index in the ZODB is a prime example, but other
examples might include a network service that only allows a certain
number of concurrent connections.  These scenarios can be helped by
quotas.

Quotas are demonstrated in the usage section.  For configuration, you
should know these characteristics:

- you cannot add a job with a quota name that is not defined in the queue;

    >>> import operator
    >>> import zc.async.job
    >>> job = zc.async.job.Job(operator.mul, 5, 2)
    >>> job.quota_names = ['content catalog']
    >>> job.quota_names
    ('content catalog',)
    >>> queue.put(job)
    Traceback (most recent call last):
    ...
    ValueError: ('unknown quota name', 'content catalog')
    >>> len(queue)
    0

- you cannot add a quota name to a job in a queue if the quota name is not
  defined in the queue;

    >>> job.quota_names = ()
    >>> job is queue.put(job)
    True
    >>> job.quota_names = ('content catalog',)
    Traceback (most recent call last):
    ...
    ValueError: ('unknown quota name', 'content catalog')
    >>> job.quota_names
    ()

- you can create and remove quotas on the queue;

    >>> list(queue.quotas)
    []
    >>> queue.quotas.create('testing')
    >>> list(queue.quotas)
    ['testing']
    >>> queue.quotas.remove('testing')
    >>> list(queue.quotas)
    []

- you can remove quotas if pending jobs have their quota names--the quota name
  is then ignored;

    >>> queue.quotas.create('content catalog')
    >>> job.quota_names = ('content catalog',)
    >>> queue.quotas.remove('content catalog')
    >>> job.quota_names
    ('content catalog',)
    >>> job is queue.claim()
    True
    >>> len(queue)
    0

- quotas default to a size of 1;

    >>> queue.quotas.create('content catalog')
    >>> queue.quotas['content catalog'].size
    1

- this can be changed at creation or later; and

    >>> queue.quotas['content catalog'].size = 2
    >>> queue.quotas['content catalog'].size
    2
    >>> queue.quotas.create('frobnitz account', size=3)
    >>> queue.quotas['frobnitz account'].size
    3

- decreasing the size of a quota while the old quota size is filled will
  not affect the currently running jobs.

    >>> job1 = zc.async.job.Job(operator.mul, 5, 2)
    >>> job2 = zc.async.job.Job(operator.mul, 5, 2)
    >>> job3 = zc.async.job.Job(operator.mul, 5, 2)
    >>> job1.quota_names = job2.quota_names = job3.quota_names = (
    ...     'content catalog',)
    >>> job1 is queue.put(job1)
    True
    >>> job2 is queue.put(job2)
    True
    >>> job3 is queue.put(job3)
    True
    >>> job1 is queue.claim()
    True
    >>> job2 is queue.claim()
    True
    >>> print queue.claim()
    None
    >>> quota = queue.quotas['content catalog']
    >>> len(quota)
    2
    >>> list(quota) == [job1, job2]
    True
    >>> quota.filled
    True
    >>> quota.size = 1
    >>> quota.filled
    True
    >>> print queue.claim()
    None
    >>> job1()
    10
    >>> print queue.claim()
    None
    >>> len(quota)
    1
    >>> list(quota) == [job2]
    True
    >>> job2()
    10
    >>> job3 is queue.claim()
    True
    >>> list(quota) == [job3]
    True
    >>> len(quota)
    1
    >>> job3()
    10
    >>> print queue.claim()
    None
    >>> len(queue)
    0
    >>> quota.clean()
    >>> len(quota)
    0
    >>> quota.filled
    False

Additional Topics: Logging and Monitoring
=========================================

XXX see monitor.txt for sketch of zc.z3monitor monitoring.

    >>> reactor.stop()

.. ......... ..
.. Footnotes ..
.. ......... ..

.. [#specific_dependencies]  More specifically, as of this writing,
    these are the minimal egg dependencies (including indirect
    dependencies):

    - pytz
        A Python time zone library
    
    - rwproperty
        A small package of desriptor conveniences
    
    - uuid
        The uuid module included in Python 2.5
    
    - zc.dict
        A ZODB-aware dict implementation based on BTrees.
    
    - zc.queue
        A ZODB-aware queue
    
    - zc.twist
        Conveniences for working with Twisted and the ZODB
    
    - zc.twisted
        A setuptools-friendly Twisted distribution, hopefully to be replaced
        with a normal Twisted distribution when it is ready.
    
    - ZConfig
        A general configuration package coming from the Zope project with which
        the ZODB tests.
    
    - zdaemon
        A general daemon tool coming from the Zope project.
    
    - ZODB3
        The Zope Object Database.
    
    - zope.bforest
        Aggregations of multiple BTrees into a single dict-like structure,
        reasonable for rotating data structures, among other purposes.
    
    - zope.component
        A way to hook together code by contract.
    
    - zope.deferredimport
        A way to defer imports in Python packages, often to prevent circular
        import problems.
    
    - zope.deprecation
        A small framework for deprecating features.
    
    - zope.event
        An exceedingly small event framework that derives its power from
        zope.component.
    
    - zope.i18nmessageid
        A way to specify strings to be translated.
    
    - zope.interface
        A way to specify code contracts and other data structures.
    
    - zope.proxy
        A way to proxy other Python objects.
    
    - zope.testing
        Testing extensions and helpers.

.. [#get_poll]

    >>> import time
    >>> def get_poll(count = None):
    ...     if count is None:
    ...         count = len(dispatcher.polls)
    ...     for i in range(30):
    ...         if len(dispatcher.polls) > count:
    ...             return dispatcher.polls.first()
    ...         time.sleep(0.1)
    ...     else:
    ...         assert False, 'no poll!'
    ... 

.. [#stop_reactor] We don't want the live dispatcher for our demos, actually.
    See dispatcher.txt to see the live dispatcher actually in use.

    >>> reactor.callFromThread(reactor.stop)
    >>> for i in range(30):
    ...     if not dispatcher.activated:
    ...         break
    ...     time.sleep(0.1)
    ... else:
    ...     assert False, 'dispatcher did not deactivate'
    ...

    Now, we'll restart with an explicit reactor.
    
    >>> import zc.async.testing
    >>> reactor = zc.async.testing.Reactor()
    >>> dispatcher.reactor = reactor
    >>> dispatcher.activate()
    >>> reactor.start()

========
zc.async
========

Goals
=====

The zc.async package provides a way to make scalable asynchronous application
calls.  Here are some example core use cases.

- You want to let users create PDFs through your application.  This can take
  quite a bit of time, and will use both system resources and one of the
  precious application threads until it is done.  Naively done, six or seven
  simultaneous PDF requests could make your application unresponsive to any
  other users.

- You want to let users spider a web site; communicate with a credit card
  company; query a large, slow LDAP database on another machine; or do
  some other action that generates network requests from the server. 
  Again, if something goes wrong, several requests could make your
  application unresponsive.

- Perhaps because of excessive conflict errors, you want to serialize work
  that can be done asynchronously, such as cataloging data.

- You want to decompose and parallelize a single job across many machines so
  it can be finished faster.

- You have an application job in the ZODB that you discover is taking
  longer than users can handle, even after you optimize it.  You want a
  quick fix to move the work out-of-band.

Many of these core use cases involve end-users being able to start potentially
expensive processes, on demand.  None of them are explicitly about scheduled
tasks, though scheduled tasks can benefit from this package.

History
=======

This is a second-generation design.  The first generation was `zasync`,
a mission-critical and successful Zope 2 product in use for a number of
high-volume Zope 2 installations.  [#history]_ It's worthwhile noting
that zc.async has absolutely no backwards comapatibility with zasync.

Design Overview
===============

Usage
-----

Looking at the design from the perspective of regular usage, code
obtains a ``queue``, which is a place to queue tasks to be performed
asynchronously.  Code calls ``put`` on the queue to register a job.  The
job must be a pickleable callable: a global function, a callable
persistent object, a method of a persistent object, or a special
zc.async.job.Job object, discussed later.  The job by default is
regsitered to be performed as soon as possible, but can be registered to
be called later.

The ``put`` call will return a zc.async.job.Job object.  This
object represents both the callable and its deferred result.  It has
information about the job requested, and the state and result of
performing the job.  An example spelling for registering a job might be
``self.pending_result = queue.put(self.performSpider)``.  The returned
object can be simply persisted and polled to see when the job
is complete; or it can be set to do tasks when it completes.

Mechanism
---------

In order for this to work, components must be set up to perform the
tasks. This part of the design has three additional kinds of participants:
agents, dispatchers, and reactors.

A dispatcher is in charge of dispatching queued work for a given
process.  It works with a mapping of queues and a reactor.  It has a
universally unique identifier (UUID), which is usually an identifier of
the application instance in which it is running.

A reactor is something that can provide an eternal loop, or heartbeat,
to power the dispatcher.  It can be the main twisted reactor (in the
main thread); another instance of a twisted reactor (in a child thread);
or any object that implements a very small subset of the twisted reactor
interface (see zc.async.interfaces.IReactor).

An agent is a persistent object in a queue that is associated with a
dispatcher and is responsible for picking jobs and keeping track of
them. Zero or more agents within a queue can be associated with a
dispatcher.  Each agent for a given dispatcher is identified uniquely
with a name [#identifying_agent]_.

Generally, these work together as follows.  The reactor calls the
dispatcher with itself and the root of the database in which the queues
are collected. The dispatcher tries to find the mapping of queues in the
root under a key of ``zc.async``.  If it finds the mapping, it iterates
over the queues (the mapping's values) and asks each queue for the
agents associated with the dispatcher's UUID.  The dispatcher then is
responsible for seeing what jobs its agents want to do from the queue,
and providing threads and connections for the work to be done.  The
dispatcher then asks the reactor to call again in a few seconds.

Set Up
======

Before we can make any calls, then, we need to set up a dispatcher, agent,
reactor, and queue.

Reactor
-------

We'll use a test reactor that we can control.

    >>> import zc.async.testing
    >>> reactor = zc.async.testing.Reactor()
    >>> reactor.start() # this mokeypatches datetime.datetime.now 

If you look at this reactor in the testing module, you can see how small
the necessary reactor interface is.  As mentioned above, many kinds of
reactors can work: the main Twisted reactor, a different Twisted reactor
instance in a child thread, or even your own reactor.  We'll have some
quick real-word examples later (XXX).  For our purposes in controling
our examples, this testing reactor has a special method that lets us
call ``reactor.time_flies(seconds)`` to perform all calls that should
happen in the next *seconds*.

Dispatcher
----------

We need to instantiate the dispatcher with a reactor and a DB.  We have the
reactor, so here is the DB.  We use a FileStorage rather than a
MappingStorage variant typical in tests and examples because we want
MVCC.

    >>> import ZODB.FileStorage
    >>> storage = ZODB.FileStorage.FileStorage(
    ...     'HistoricalConnectionTests.fs', create=True)
    >>> from ZODB.DB import DB 
    >>> db = DB(storage) 
    >>> conn = db.open()
    >>> root = conn.root()

The dispatcher will look for a UUID utility.
    
    >>> from zc.async.instanceuuid import UUID
    >>> import zope.component
    >>> zope.component.provideUtility(
    ...     UUID, zc.async.interfaces.IUUID, '')

Now we can instantiate.

    >>> import zc.async.dispatcher
    >>> dispatcher = zc.async.dispatcher.Dispatcher(reactor, db)

The dispatcher knows its UUID.  This is usually a UUID of the process,
and of the instance.  The instance UUID, in hex, is stored in
INSTANCE_HOME/etc/uuid.txt

    >>> import uuid
    >>> import os
    >>> f = open(os.path.join(
    ...     os.environ.get("INSTANCE_HOME"), 'etc', 'uuid.txt'))
    >>> uuid_hex = f.readline().strip()
    >>> f.close()
    >>> uuid = uuid.UUID(uuid_hex)
    >>> dispatcher.UUID == uuid
    True

(The uuid.txt file is intended to stay in the instance home as a
persistent identifier.)

If you don't want this default UUID, you can pass one in to the constructor.

The dispatcher also has a configuration value, ``poll_interval``.  This
value indicates how often in seconds, approximately, the dispatcher
should poll queues for work.  It defaults to 5 seconds.

    >>> dispatcher.poll_interval
    5

Now we'll activate the dispatcher and let it poll.

    >>> dispatcher.activate()
    >>> reactor.time_flies(1)
    1

Note that the dispatcher didn't complain even though the ``zc.async``
key does not exist in the root.

The dispatcher has tried to poll once, to no effect.

    >>> import datetime
    >>> import pytz
    >>> len(dispatcher.polls)
    1
    >>> poll = dispatcher.polls.first()
    >>> poll.utc_timestamp <= datetime.datetime.utcnow()
    True
    >>> poll
    {}

The ``dispatcher.polls.first()`` poll always contains information about
the dispatcher's most recent poll, if any.  The ``utc_timestamp`` is the
UTC timestamp of the (end of the) last poll. The ``polls`` object is a
(non-persistent) data structure documenting approximately the last 24 hours
of polls.  View and change this with the ``period`` value of the polls
object.

    >>> dispatcher.polls.period
    datetime.timedelta(1)

Each poll is represented with a mapping, with keys of queue keys in
the root queue mapping.  The values are mappings of agents that were
polled, where the key is the agent name and the value is a data object
describing what was done for the agent.

Queue
-----

Now let's create the mapping of queues, and a single queue.

    >>> import zc.async.queue
    >>> import zc.async.interfaces
    >>> mapping = root[zc.async.interfaces.KEY] = zc.async.queue.Queues()
    >>> queue = mapping[''] = zc.async.queue.Queue()
    >>> import transaction
    >>> transaction.commit()

Now we have created everything except an agent for this dispatcher in the
queue.  If we let the reactor run, the queue will be checked, but nothing
will have been done, because no agents were found.

    >>> reactor.time_flies(dispatcher.poll_interval)
    1
    >>> len(dispatcher.polls)
    2
    >>> import pprint
    >>> pprint.pprint(dispatcher.polls.first())
    {'': {}}

Well, actually, a bit more than nothing was done.

- The dispatcher registered and activated itself with the queue.

- The queue fired events to announce the dispatcher's registration and
  activation.  We could have registered subscribers for either or both
  of these events to create agents.
  
  Note that the dispatcher in queue.dispatchers is a persistent
  representative of the actual dispatcher: they are different objects.

- Lastly, the dispatcher made its first ping.  A ping means that the
  dispatcher changes a datetime to record that it is alive.  

  The dispatcher needs to update its last_ping after every ``ping_interval``
  seconds.  If it has not updated the last_ping after ``ping_death_interval``
  then the dispatcher is considered to be dead, and active jobs in the
  dispatcher's agents are ended (and given a chance to respond to that status
  change, so they can put themselves back on the queue to be restarted if
  desired).

These are demonstrated in dispatcher.txt.

Agent
-----

As mentioned above, we could have registered a subscriber for either or
both of the registration and activation events to create agents.  For
this example, though, we'll add an agent manually.

Agents are responsible for getting the next job from the queue and for
specifying how many worker threads they should use at once.  We'll use
the defaults for now to create an agent that simply gets the next
available FIFO job, and has a maximum of three worker threads.

    >>> import zc.async.agent
    >>> agent = zc.async.agent.Agent()
    >>> queue.dispatchers[dispatcher.UUID]['main'] = agent
    >>> agent.chooser is zc.async.agent.chooseFirst
    True
    >>> agent.size
    3
    >>> transaction.commit()

Now if we poll, the agent will be included, thought there are still no jobs
to be done.

    >>> reactor.time_flies(dispatcher.poll_interval)
    1
    >>> len(dispatcher.polls)
    3
    >>> dispatcher.polls.first()
    {'': {'main': {'new_jobs': [], 'error': None, 'len': 0, 'size': 3}}}

It took awhile to explain it, but we now have a simple set up: a queue,
a dispatcher with reactor, and an agent.  Let's start doing the easy and
fun part: making some asynchronous calls!

Basic Usage: IQueue.put
=========================

The simplest case is simple to perform: pass a persistable callable to the
queue's `put` method.  We'll need some adapters to make this happen
[#setup_adapters]_.

    >>> def send_message():
    ...     print "imagine this sent a message to another machine"
    >>> job = queue.put(send_message)
    >>> transaction.commit()

Now we need to wait for the poll to happen again, and then wait for the job
to be completed in a worker thread.

    >>> import time
    >>> def wait_for(*jobs, **kwargs):
    ...     reactor.time_flies(dispatcher.poll_interval) # starts thread
    ...     # now we wait for the thread
    ...     for i in range(kwargs.get('attempts', 10)):
    ...         while reactor.time_passes():
    ...             pass
    ...         transaction.begin()
    ...         for j in jobs:
    ...             if j.status != zc.async.interfaces.COMPLETED:
    ...                 break
    ...         else:
    ...             break
    ...         time.sleep(0.1)
    ...     else:
    ...         print 'TIME OUT'
    ...
    >>> wait_for(job)
    imagine this sent a message to another machine

We also could have used the method of a persistent object.  Here's another
quick example.

    >>> import persistent
    >>> class Demo(persistent.Persistent):
    ...     counter = 0
    ...     def increase(self, value=1):
    ...         self.counter += value
    ...
    >>> root['demo'] = Demo()
    >>> transaction.commit()
    >>> root['demo'].counter
    0
    >>> job = queue.put(root['demo'].increase)
    >>> transaction.commit()
    >>> wait_for(job)
    >>> root['demo'].counter
    1

The method was called, and the persistent object modified!

You can also pass a datetime.datetime to schedule a call.  A datetime
without a timezone is considered to be in the UTC timezone.

    >>> t = transaction.begin()
    >>> import datetime
    >>> import pytz
    >>> datetime.datetime.now(pytz.UTC)
    datetime.datetime(2006, 8, 10, 15, 44, 43, 211, tzinfo=<UTC>)
    >>> job = queue.put(
    ...     send_message, datetime.datetime(
    ...         2006, 8, 10, 15, 56, tzinfo=pytz.UTC))
    >>> job.begin_after
    datetime.datetime(2006, 8, 10, 15, 56, tzinfo=<UTC>)
    >>> transaction.commit()
    >>> wait_for(job, attempts=1) # +5 virtual seconds
    TIME OUT
    >>> wait_for(job, attempts=1) # +5 virtual seconds
    TIME OUT
    >>> zc.async.testing.set_now(datetime.datetime(
    ...     2006, 8, 10, 15, 56, tzinfo=pytz.UTC))
    >>> wait_for(job) # +5 virtual seconds
    imagine this sent a message to another machine
    >>> datetime.datetime.now(pytz.UTC) >= job.begin_after
    True

If you set a time that has already passed, it will be run as if it had
been set to run immediately.

    >>> t = transaction.begin()
    >>> job = queue.put(
    ...     send_message, datetime.datetime(2006, 8, 10, 15, tzinfo=pytz.UTC))
    >>> transaction.commit()
    >>> wait_for(job)
    imagine this sent a message to another machine

...unless the job has already timed out, in which case the job fails
with an abort.

    >>> t = transaction.begin()
    >>> job = queue.put(
    ...     send_message, datetime.datetime(2006, 7, 21, 12, tzinfo=pytz.UTC))
    >>> transaction.commit()
    >>> wait_for(job)
    >>> job.result
    <twisted.python.failure.Failure zc.async.interfaces.AbortedError>
    >>> import sys
    >>> job.result.printTraceback(sys.stdout) # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    Failure: zc.async.interfaces.AbortedError:

The queue's `put` method is the essential API.  Other methods are used
to introspect, but are not needed for basic usage.

But what is that result of the `put` call in the examples above?  A
job?  What do you do with that?

Jobs
====

The result of a call to `put` returns an IJob.  The
job represents the pending result.  This object has a lot of
functionality that's explored in other documents in this package, and
demostrated a bit below, but here's a summary.  

- You can introspect it to look at, and even modify, the call and its
  arguments.

- You can specify that the job should be run serially with others
  of a given identifier.

- You can specify that the job may or may not be run by given
  workers (identifying them by their UUID).

- You can specify other calls that should be made on the basis of the
  result of this call.

- You can persist a reference to it, and periodically (after syncing
  your connection with the database, which happens whenever you begin or
  commit a transaction) check its `state` to see if it is equal to
  zc.async.interfaces.COMPLETED.  When it is, the call has run to
  completion, either to success or an exception.

- You can look at the result of the call (once COMPLETED).  It might be
  the result you expect, or a twisted.python.failure.Failure, which is a
  way to safely communicate exceptions across connections and machines
  and processes.

So here's a simple story.  What if you want to get a result back from a
call?  Look at the job.result after the call is COMPLETED.

    >>> def imaginaryNetworkCall():
    ...     # let's imagine this makes a network call...
    ...     return "200 OK"
    ...
    >>> job = queue.put(imaginaryNetworkCall)
    >>> print job.result
    None
    >>> job.status == zc.async.interfaces.PENDING
    True
    >>> transaction.commit()
    >>> wait_for(job)
    >>> t = transaction.begin()
    >>> job.result
    '200 OK'
    >>> job.status == zc.async.interfaces.COMPLETED
    True

What's more, you can pass a Job to the `put` call.  This means that
you aren't constrained to simply having simple non-argument calls
performed asynchronously, but you can pass a job with a call,
arguments, and keyword arguments.  Here's a quick example.  We'll use
the demo object, and its increase method, that we introduced above, but
this time we'll include some arguments [#job]_.

With placeful arguments:

    >>> t = transaction.begin()
    >>> job = queue.put(
    ...     zc.async.job.Job(root['demo'].increase, 5))
    >>> transaction.commit()
    >>> wait_for(job)
    >>> t = transaction.begin()
    >>> root['demo'].counter
    6

With keyword arguments:

    >>> job = queue.put(
    ...     zc.async.job.Job(root['demo'].increase, value=10))
    >>> transaction.commit()
    >>> wait_for(job)
    >>> t = transaction.begin()
    >>> root['demo'].counter
    16

Note that arguments to these jobs can be any persistable object.

What happens if a call raises an exception?  The return value is a Failure.

    >>> def I_am_a_bad_bad_function():
    ...     return foo + bar
    ...
    >>> job = queue.put(I_am_a_bad_bad_function)
    >>> transaction.commit()
    >>> wait_for(job)
    >>> t = transaction.begin()
    >>> job.result
    <twisted.python.failure.Failure exceptions.NameError>

Failures can provide useful information such as tracebacks.

    >>> print job.result.getTraceback()
    ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    exceptions.NameError: global name 'foo' is not defined
    <BLANKLINE>

zc.async.local
==============

Jobs always run their callables in a thread, within the context of a
connection to the ZODB. The callables have access to three special
thread-local functions if they need them for special uses.  These are
available off of zc.async.local.

zc.async.local.getJob()
    The getJob function can be used to examine the job, to get
    a connection off of _p_jar, to get the queue into which the job
    was put, or other uses.

zc.async.local.setLiveAnnotation(name, value[, job])
    The setLiveAnnotation tells the agent to set an annotation on a job,
    by default the current job, *in another connection*.  This makes it
    possible to send messages about progress or for coordination while in the
    middle of other work.  *For safety, do not send mutables or a persistent
    object.*

zc.async.local.getLiveAnnotation(name[, job[, default=None[, block=False]]])
    The getLiveAnnotation tells the agent to get an annotation for a job,
    by default the current job, *from another connection*.  This makes it
    possible to send messages about progress or for coordination while in the
    middle of other work.  *For safety, if you get a mutable, do not mutate
    it.*  If the value is a persistent object, it will not be returned: you
    will get a Fault object instead.  If the ``block`` argument is True,
    the function will wait until an annotation of the given name is available.
    Otherwise, it will return the ``default`` if the name is not present in the
    annotations.

The last two functions can even be passed to a thread that does not have
a connection.  Note that this is not intended as a way to communicate across
threads on the same process, but across processes.

Let's give these a whirl.  We will write a function that examines the
job's state while it is being called, and sets the state in an
annotation, then waits for our flag to finish.

    >>> def annotateStatus():
    ...     zc.async.local.setLiveAnnotation(
    ...         'zc.async.test.status',
    ...         zc.async.local.getJob().status)
    ...     zc.async.local.getLiveAnnotation(
    ...         'zc.async.test.flag', timeout=5)
    ...     return 42
    ...
    >>> job = queue.put(annotateStatus)
    >>> transaction.commit()
    >>> def wait_for_annotation(job, key):
    ...     reactor.time_flies(dispatcher.poll_interval) # starts thread
    ...     for i in range(10):
    ...         while reactor.time_passes():
    ...             pass
    ...         transaction.begin()
    ...         if key in job.annotations:
    ...             break
    ...         time.sleep(0.1)
    ...     else:
    ...         print 'Timed out' + repr(dict(job.annotations))
    ...
    >>> wait_for_annotation(job, 'zc.async.test.status')
    >>> job.annotations['zc.async.test.status'] == (
    ...     zc.async.interfaces.ACTIVE)
    True
    >>> job.status == zc.async.interfaces.ACTIVE
    True
    >>> job.annotations['zc.async.test.flag'] = True
    >>> transaction.commit()
    >>> wait_for(job)
    >>> job.result
    42

Job Callbacks
=============

You can register callbacks to handle the result of a job, whether a
Failure or another result.  These callbacks can be thought of as the
"except" "else" or "finally" clauses of a "try" statement.  Each
callback receives the job's current result as input, and its output
becomes the job's new result (and therefore the input of the next
callback, if any).

Note that, during execution of a callback, there is no guarantee that
the callback will be processed on the same machine as the main call.  Also,
the ``local`` functions will not work.

Here's a simple example of reacting to a success.

    >>> def I_scribble_on_strings(string):
    ...     return string + ": SCRIBBLED"
    ...
    >>> job = queue.put(imaginaryNetworkCall)
    >>> callback = job.addCallback(I_scribble_on_strings)
    >>> transaction.commit()
    >>> wait_for(job)
    >>> job.result
    '200 OK'
    >>> callback.result
    '200 OK: SCRIBBLED'

Here's a more complex example of handling a Failure, and then chaining
a subsequent callback.

    >>> def I_handle_NameErrors(failure):
    ...     failure.trap(NameError) # see twisted.python.failure.Failure docs
    ...     return 'I handled a name error'
    ...
    >>> job = queue.put(I_am_a_bad_bad_function)
    >>> callback1 = job.addCallbacks(failure=I_handle_NameErrors)
    >>> callback2 = callback1.addCallback(I_scribble_on_strings)
    >>> transaction.commit()
    >>> wait_for(job)
    >>> job.result
    <twisted.python.failure.Failure exceptions.NameError>
    >>> callback1.result
    'I handled a name error'
    >>> callback2.result
    'I handled a name error: SCRIBBLED'

Enforced Serialization
======================

One class of asynchronous jobs are ideally serialized.  For instance,
you may want to reduce or eliminate the chance of conflict errors when
updating a text index.  One way to do this kind of serialization is to
use the ``quota_names`` attribute of the job.

For example, let's first show two non-serialized jobs running at the
same time, and then two serialized jobs created at the same time.

For our parallel jobs, we'll do something that would create a deadlock
if they were serial.  Notice that we are mutating the job arguments after
creation to accomplish this, which is supported.

    >>> def waitForParallel(other):
    ...     zc.async.local.setLiveAnnotation(
    ...         'zc.async.test.flag', True)
    ...     zc.async.local.getLiveAnnotation(
    ...         'zc.async.test.flag', other, block=True)
    ...
    >>> job1 = queue.put(waitForParallel)
    >>> job2 = queue.put(waitForParallel)
    >>> job1.args.append(job2)
    >>> job2.args.append(job1)
    >>> transaction.commit()
    >>> wait_for(job1, job2)
    >>> job1.status == zc.async.interfaces.COMPLETED
    True
    >>> job2.status == zc.async.interfaces.COMPLETED
    True

On the other hand, for our serial jobs, we'll do something that would fail
if it were parallel.

    >>> def pause(other):
    ...     zc.async.local.setLiveAnnotation(
    ...         'zc.async.test.flag', True)
    ...     res = zc.async.local.getLiveAnnotation(
    ...         'zc.async.test.flag', timeout=0.4, poll=0.1, job=other)
    ...
    >>> job1 = queue.put(pause)
    >>> job2 = queue.put(imaginaryNetworkCall)
    >>> job1.quota_names = ('test',)
    Traceback (most recent call last):
    ...
    ValueError: quota name not defined in queue
    >>> queue.quotas.create('test')
    >>> job1.quota_names = ('test',)
    >>> job2.quota_names = ('test',)
    >>> job1.args.append(job2)
    >>> job2.args.append(job1)
    >>> transaction.commit()
    >>> reactor.time_flies(dispatcher.poll_interval)
    1
    >>> for i in range(10):
    ...     t = transaction.begin()
    ...     if job1.status == zc.async.interfaces.ACTIVE:
    ...         break
    ...     time.sleep(0.1)
    ... else:
    ...     print 'TIME OUT'
    ...
    >>> job2.status == zc.async.interfaces.PENDING
    True
    >>> job2.annotations['zc.async.test.flag'] = False
    >>> transaction.commit()
    >>> wait_for(job1)
    >>> wait_for(job2)

Returning Jobs
==============

Our examples so far have done work directly.  What if the job wants to
orchestrate other work?  One way this can be done is to return another
job.  The result of the inner job will be the result of the first
job once the inner job is finished.  This approach can be used to
break up the work of long running processes; to be more cooperative to
other jobs; and to make parts of a job that can be parallelized available
to more workers.

Serialized Work
---------------

First, consider a serialized example.  This simple pattern is one approach.

    >>> def second_job(value):
    ...     # imagine a lot of work goes on...
    ...     return value * 2
    ...
    >>> def first_job():
    ...     # imagine a lot of work goes on...
    ...     intermediate_value = 21
    ...     queue = zc.async.local.getJob().queue
    ...     return queue.put(zc.async.job.Job(
    ...         second_job, intermediate_value))
    ...
    >>> job = queue.put(first_job)
    >>> transaction.commit()
    >>> wait_for(job, attempts=3)
    TIME OUT
    >>> wait_for(job, attempts=3)
    >>> job.result
    42

The second_job could also have returned a job, allowing for additional
legs.  Once the last job returns a real result, it will cascade through the
past jobs back up to the original one.

A different approach could have used callbacks.  Using callbacks can be
somewhat more complicated to follow, but can allow for a cleaner
separation of code: dividing code that does work from code that
orchestrates the jobs.  We'll see an example of the idea below.

Parallelized Work
-----------------

Now how can we set up parallel jobs?  There are other good ways, but we
can describe one way that avoids potential problems with the
current-as-of-this-writing (ZODB 3.8 and trunk) default optimistic MVCC
serialization behavior in the ZODB.  The solution uses callbacks, which
also allows us to cleanly divide the "work" code from the synchronization
code, as described in the previous paragraph.

First, we'll define the jobs that do work.  ``job_A``, ``job_B``, and
``job_C`` will be jobs that can be done in parallel, and
``post_process`` will be a function that assembles the job results for a
final result.

    >>> def job_A():
    ...     # imaginary work...
    ...     return 7
    ...
    >>> def job_B():
    ...     # imaginary work...
    ...     return 14
    ...
    >>> def job_C():
    ...     # imaginary work...
    ...     return 21
    ...
    >>> def post_process(*args):
    ...     # this callable represents one that needs to wait for the
    ...     # parallel jobs to be done before it can process them and return
    ...     # the final result
    ...     return sum(args)
    ...

Now this code works with jobs to get everything done.  Note, in the
callback function, that mutating the same object we are checking
(job.args) is the way we are enforcing necessary serializability
with MVCC turned on.

    >>> def callback(job, result):
    ...     job.args.append(result)
    ...     if len(job.args) == 3: # all results are in
    ...         zc.async.local.getJob().queue.put(job)
    ...     return result # unnecessary; just keeps this job's result
    ...     # from changing
    ...
    >>> def main_job():
    ...     job = zc.async.job.Job(post_process)
    ...     queue = zc.async.local.getJob().queue
    ...     for j in (job_A, job_B, job_C):
    ...         queue.put(j).addCallback(
    ...             zc.async.job.Job(callback, job))
    ...     return job
    ...

Now we'll put this in and let it cook.

    >>> job = queue.put(main_job)
    >>> transaction.commit()
    >>> wait_for(job, attempts=3)
    TIME OUT
    >>> wait_for(job, attempts=3)
    TIME OUT
    >>> wait_for(job, attempts=3)
    TIME OUT
    >>> wait_for(job, attempts=3)
    >>> job.result
    42

Ta-da!

A further polish to this solution would eliminate the chance for conflict
errors by making the callbacks put their work into jobs with
serialized_ids.  You'd also probably want to deal with the possibility of
one or more of the jobs generating a Failure.

Returning Deferreds
===================

What if you want to do work that doesn't require a ZODB connection?  You
can also return a Twisted deferred (twisted.internet.defer.Deferred).
When you then ``callback`` the deferred with the eventual result, the
agent will be responsible for setting that value on the original
deferred and calling its callbacks.  This can be a useful trick for
making network calls using Twisted or zc.ngi, for instance.

    >>> def imaginaryNetworkCall2(deferred):
    ...     # make a network call...
    ...     deferred.callback('200 OK')
    ...
    >>> import twisted.internet.defer
    >>> import threading
    >>> def delegator():
    ...     deferred = twisted.internet.defer.Deferred()
    ...     t = threading.Thread(
    ...         target=imaginaryNetworkCall2, args=(deferred,))
    ...     t.run()
    ...     return deferred
    ...
    >>> job = queue.put(delegator)
    >>> transaction.commit()
    >>> wait_for(job)
    >>> job.result
    '200 OK'

Logging Agents
==============

Agents log when they get a job and when they complete a job.  They also can
log every given number of polls.

Additional Agents
=================

A process can host many different agents, and many processes can provide
workers for a queue.

Handling Failed Agents
======================

...worker finds another process already installed with same UUID and
name; could be shutdown error (ghost of self) or really another
process...show engineUUID... some discussion already in
datamanager.txt...

Advice
======

Avoid Conflict Errors
---------------------

...try to only mutate job, or contemplate serializing...

Gotchas
=======

...some callbacks may still be working when job is completed.  Therefore
job put in `completed` for worker so that it can have a chance to run to
completion.

    >>> reactor.stop()

=========
Footnotes
=========

.. [#other_packages] Another Zope 3 package that approaches somewhat
    similar use cases to these is lovely.remotetask
    (http://svn.zope.org/lovely.remotetask/).
    
    Another set of use cases center around scheduling: we need to retry an
    asynchronous task after a given amount of time; or we want to have a
    requested job happen late at night; or we want to have a job happen
    regularly.  The Zope 3 scheduler
    (http://svn.zope.org/Zope3/trunk/src/scheduler/) approaches the last of
    these tasks with more infrastructure than zc.async, as arguably does a
    typical "cron wget" approach.  However, both approaches are prone to
    serious problems when the scheduled task takes more time than expected,
    and one instance of a task overlaps the previous one, sometimes causing
    disastrous problems.  By using zc.async jobs to represent the
    pending result, and even to schedule the next call, this problem can be
    alleviated.

.. [#history] The first generation, zasync, had the following goals:

    - be scalable, so that another process or machine could do the
      asynchronous work;

    - support lengthy jobs outside of the ZODB;

    - support lengthy jobs inside the ZODB;

    - be recoverable, so that crashes would not lose work;

    - be discoverable, so that logs and web interfaces give a view into
      the work being done asynchronously;

    - be easily extendible, to do new jobs; and

    - support graceful job expiration and cancellation.

    It met its goals well in some areas and adequately in others.

    Based on experience with the first generation, this second
    generation identifies several areas of improvement from the first
    design, and adds several goals.

    - Improvements

      * More carefully delineate the roles of the comprising components.

        The zasync design has three main components, as divided by their
        roles: persistent deferreds, now called jobs; job queues (the
        original zasync's "asynchronous call manager"); and asynchronous
        workers (the original zasync ZEO client).  The zasync 1.x design
        blurred the lines between the three components such that the
        component parts could only be replaced with difficulty, if at
        all. A goal for the 2.x design is to clearly define the role for
        each of three components such that, for instance, a user of a
        queue does not need to know about the dispatcher ot the agents.

      * Improve scalability of asynchronous workers.

        The 1.x line was initially designed for a single asynchronous
        worker, which could be put on another machine thanks to ZEO. 
        Tarek Ziadé of Nuxeo wrote zasyncdispatcher, which allowed
        multiple asynchronous workers to accept work, allowing multiple
        processes and multiple machines to divide and conquer. It worked
        around the limitations of the original zasync design to provide
        even more scalability. However, it was forced to divide up work
        well before a given worker looks at the queue.

        While dividing work earlier allows guesses and heuristics a
        chance to predict what worker might be more free in the future,
        a more reliable approach is to let the worker gauge whether it
        should take a job at the time the job is taken. Perhaps the
        worker will choose based on the worker's load, or other
        concurrent jobs in the process, or other details. A goal for the
        2.x line is to more directly support this type of scalability.

      * Improve scalability of registering jobs.

        The 1.x line initially wasn't concerned about very many
        concurrent asynchronous requests.  When this situation was
        encountered, it caused ConflictErrors between the worker process
        reading the deferred queue and the code that was adding the
        deferreds.  Thanks to Nuxeo, this problem was addressed in the
        1.x line.  A goal for the new version is to include and improve
        upon the 1.x solution.

      * Make it even simpler to provide new jobs.

        In the first version, `plugins` performed jobs.  They had a
        specific API and they had to be configured.  A goal for the new
        version is to require no specific API for jobs, and to not
        require any configuration.

      * Improve report information, especially through the web.

        The component that the first version of zasync provided to do
        the asynchronous work, the zasync client, provided very verbose
        logs of the jobs done, but they were hard to read and also did
        not have a through- the-web parallel.  Two goals for the new
        version are to improve the usefulness of the filesystem logs and
        to include more complete through-the-web visibility of the
        status of the provided asynchronous clients.

      * Make it easier to configure and start, especially for small
        deployments.

        A significant barrier to experimentation and deployment of the
        1.x line was the difficulty in configuration.  The 1.x line
        relied on ZConfig for zasync client configuration, demanding
        non-extensible similar-yet-subtly-different .conf files like the
        Zope conf files. The 2.x line plans to provide code that Zope 3
        can configure to run in the same process as a standard Zope 3
        application.  This means that development instances can start a
        zasync quickly and easily.  It also means that processes can be
        reallocated on the fly during production use, so that a machine
        being used as a zasync process can quickly be converted to a web
        server, if needed, and vice versa.  It further means that the
        Zope web server can be used for through-the-web reports of the
        current zasync process state.

    - New goals

      * Support intermediate return calls so that jobs can report back
        how they are doing.

        A frequent request from users of zasync 1.x was the ability for
        a long- running asynchronous process to report back progress to
        the original requester.  The 2.x line addresses this with three
        changes:

        + jobss are annotatable;

        + jobs should not be modified in an asynchronous
          worker that does work (though they may be read);

        + jobs can request another job in a synchronous process
          that annotates the job with progress status or other
          information.

        Because of relatively recent changes in ZODB--multi version
        concurrency control--this simple pattern should not generate
        conflict errors.

      * Support time-delayed calls.

        Retries and other use cases make time-delayed deferred calls
        desirable. The new design supports these sort of calls.

.. [#identifying_agent] Generally, the combination of a queue name plus a
    dispatcher UUID plus an agent name uniquely identifies an agent.

.. [#uuid] UUIDs are generated by http://zesty.ca/python/uuid.html, as
    incorporated in Python 2.5.  They are expected to be found in 
    os.path.join(os.environ.get("INSTANCE_HOME"), 'etc', 'uuid.txt');
    this file will be created and populated with a new UUID if it does
    not exist.

.. [#subscribers] The zc.async.subscribers module provides two different
    subscribers to set up a datamanager.  One subscriber expects to put
    the object in the same database as the main application
    (`zc.async.subscribers.basicInstallerAndNotifier`).  This is the
    default, and should probably be used if you are a casual user.
    
    The other subscriber expects to put the object in a secondary
    database, with a reference to it in the main database
    (`zc.async.subscribers.installerAndNotifier`).  This approach keeps
    the database churn generated by zc.async, which can be significant,
    separate from your main data.  However, it also requires that you
    set up two databases in your zope.conf (or equivalent, if this is
    used outside of Zope 3).  And possibly even more onerously, it means
    that persistent objects used for calls must either already be
    committed, or be explicitly added to a connection; otherwise you
    will get an InvalidObjectReference (see
    cross-database-references.txt in the ZODB package).  The possible
    annoyances may be worth it to someone building a more demanding
    application.
    
    Again, the first subscriber is the easier to use, and is the default.
    You can use either one (or your own).

    If you do want to use the second subscriber, here's a start on what
    you might need to do in your zope.conf.  In a Zope without ZEO you
    would set something like this up.

    <zodb>
      <filestorage>
        path $DATADIR/Data.fs
      </filestorage>
    </zodb>
    <zodb zc.async>
      <filestorage>
        path $DATADIR/zc.async.fs
      </filestorage>
    </zodb>

    For ZEO, you could have the two databases on one server...
    
    <filestorage 1>
      path Data.fs
    </filestorage>
    <filestorage 2>
      path zc.async.fs
    </filestorage>
    
    ...and then set up ZEO clients something like this.
    
    <zodb>
      <zeoclient>
        server localhost:8100
        storage 1
        # ZEO client cache, in bytes
        cache-size 20MB
      </zeoclient>
    </zodb>
    <zodb zc.async>
      <zeoclient>
        server localhost:8100
        storage 2
        # ZEO client cache, in bytes
        cache-size 20MB
      </zeoclient>
    </zodb>

.. [#setup_adapters]

    You must have two adapter registrations: IConnection to
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

    We need to be able to get data manager partials for functions and methods;
    normal partials for functions and methods; and a data manager for a partial.
    Here are the necessary registrations.

    >>> import zope.component
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

.. [#handlers] In the second footnote above, the text describes two
    available subscribers.  When this documentation is run as a test, it
    is run twice, once with each.  To accomodate this, in our example
    below we appear to pull the "installerAndNotifier" out of the air:
    it is installed as a global when the test is run.

.. [#job] The Job class can take arguments and keyword arguments
    for the wrapped callable at call time as well, similar to Python
    2.5's `partial`.  This will be important when we use the Job as
    a callback.  For this use case, though, realize that the job
    will be called with no arguments, so you must supply all necessary
    arguments for the callable on creation time.

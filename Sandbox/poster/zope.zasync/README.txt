================================================================
zasync 2.0: A ZODB Framework for Asynchronous Calls
================================================================

Frequently a ZODB transaction should complete quickly but request work to be
done elsewhere--in another thread, another process, or another machine.
Using a model similar to and inspired by the Twisted framework's deferred,
the zasync package provides various components that can be assembled to make
this possible in flexible ways.

Goals and History
=================

This is a second-generation design.  The first generation, a mission-critical
and successful Zope 2 product in use for a number of high-volume Zope 2
installations, had the following goals:

- be scalable, so that another process or machine could do the asynchronous
  work;

- support lengthy jobs outside of the ZODB;

- support lengthy jobs inside the ZODB;

- be recoverable, so that crashes would not lose work;

- be discoverable, so that logs and web interfaces give a view into the work
  being done asynchronously;

- be easily extendible, to do new jobs; and

- support graceful job expiration and cancellation.

It met its goals well in some areas and adequately in others.

Based on experience with the first generation, this second generation
identifies several areas of improvement from the first design, and adds
several goals.

- Improvements

  * More carefully delineate the roles of the comprising components.

    The zasync design has three main components, as divided by their roles:
    persistent deferreds, persistent deferred queues (the original zasync's
    "asynchronous call manager"), and asynchronous workers (the original
    zasync ZEO client).  The zasync 1.x design blurred the lines between the
    three components such that the component parts could only be replaced
    with difficulty, if at all. A goal for the 2.x design is to clearly define
    the role for each of three components such that, for instance, a user of a
    persistent deferred does not need to know about the persistent deferred
    queue and in fact should not assume that it is the mechanism by which the
    persistent deferred will be performed.

  * Improve scalability of asynchronous workers.

    The 1.x line was initially designed for a single asynchronous worker,
    which could be put on another machine thanks to ZEO.  Tarek Ziadé of
    Nuxeo wrote zasyncdispatcher, which allowed multiple asynchronous workers
    to accept work, allowing multiple processes and multiple machines to
    divide and conquer. It worked around the limitations of the original
    zasync design to provide even more scalability. However, it was forced to
    divide up work well before a given worker looks at the queue.

    While dividing work earlier allows guesses and heuristics a chance to
    predict what worker might be more free in the future, a more reliable
    approach is to let the worker gauge whether it should take a job at the
    time the job is taken. Perhaps the worker will choose based on the
    worker's load, or other concurrent jobs in the process, or other details.
    A goal for the 2.x line is to more directly support this type of
    scalability.

  * Improve scalability of registering deferreds.

    The 1.x line initially wasn't concerned about very many concurrent
    asynchronous requests.  When this situation was encountered, it caused
    ConflictErrors between the worker process reading the deferred queue
    and the code that was adding the deferreds.  Thanks to Nuxeo, this
    problem was addressed in the 1.x line.  A goal for the new version
    is to include and improve upon the 1.x solution.

  * Make it even simpler to provide new jobs.

    In the first version, `plugins` performed jobs.  They had a specific
    API and they had to be configured.  A goal for the new version is to
    require no specific API for jobs, and to not require any configuration.

  * Improve report information, especially through the web.

    The component that the first version of zasync provided to do the
    asynchronous work, the zasync client, provided very verbose logs of the
    jobs done, but they were hard to read and also did not have a through-
    the-web parallel.  Two goals for the new version are to improve the
    usefulness of the filesystem logs and to include more complete
    through-the-web visibility of the status of the provided asynchronous
    clients.

  * Make it easier to configure and start, especially for small deployments.

    A significant barrier to experimentation and deployment of the 1.x line
    was the difficulty in configuration.  The 1.x line relied on ZConfig
    for zasync client configuration, demanding non-extensible
    similar-yet-subtly-different .conf files like the Zope conf files.
    The 2.x line plans to provide code that Zope 3 can configure to run in
    the same process as a standard Zope 3 application.  This means that
    development instances can start a zasync quickly and easily.  It also
    means that processes can be reallocated on the fly during production use,
    so that a machine being used as a zasync process can quickly be converted
    to a web server, if needed, and vice versa.  It further means that the
    Zope web server can be used for through-the-web reports of the current
    zasync process state.

- New goals

  * Support intermediate return calls so that jobs can report back how they
    are doing.

    A frequent request from users of zasync 1.x was the ability for a long-
    running asynchronous process to report back progress to the original
    requester.  The 2.x line expects to address this with three changes:

    + persistent deferreds should be annotatable;

    + persistent deferreds should not be modified in an asynchronous
      job that does work (though they may be read);

    + jobs can request another deferred in a synchronous process that
      annotates the deferred with progress status or other information.

    Because of relatively recent changes in ZODB--multi version concurrency
    control--this simple pattern should not generate conflict errors.

  * Support time-delayed calls.

    Retries and other use cases make time-delayed deferred calls desirable.
    The new design will attempt to support these sort of calls.

It's worthwhile noting that the 2.x design has absolutely no backwards
comapatibility from the 1.x code.

The Three Core Components
=========================

Persistent deferreds, a persistent deferred queue, and a set of asynchronous
workers comprise the three core components of zasync 2.1.  Code that
receives a persistent deferred should not assume that the work will
necessarily be performed by the persistent deferred queue defined here.
Similarly, the code using the persistent deferred queue should not assume that
the workers are as described here.  Each layer is a black box to client code.

Persistent deferreds
--------------------

Persistent deferreds have an interface similar to Twisted deferreds, but with
some important differences.

Asynchronous tasks
------------------

Common helpers: do a job in ZODB; do a job in a security context

Asynchronous task queue
---------------------

A Zope 3 persistent utility...

Asynchronous worker
-------------------

XXX

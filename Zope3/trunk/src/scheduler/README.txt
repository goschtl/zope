==================
The Task Scheduler
==================


  >>> def callable(*args, **kw):
  ...     print 'I have been called.'


The API
-------

From a high-level point of view, the developer starts out by developing their
own or us an existing task component:

  >>> from scheduler import task
  >>> from twisted.internet import reactor

  >>> class MyTask(task.Task):
  ...
  ...     def computeDelayToNextCall(self):
  ...         return 88

  >>> mytask = MyTask(callable, ('arg1', 'arg2'), {'kw1': 1, 'kw2': 2})

As you can see, you only need to implement the ``computeDelayToNextCall()``
method that used by the rescheduling mechism to determine the next time of
execution. It is up to the developer to compute the delay, which is specified
in seconds. Based on the system you are running on, a float for the delay
allows you to specify sub-second intervals.

So, now we have a task, but it has not been started:

  >>> mytask.running
  False
  >>> mytask.count

Now that you have a task component, we register it as a utility providing
``ITask``.

  >>> from zope.app.testing import ztapi
  >>> from scheduler import interfaces
  >>> ztapi.provideUtility(interfaces.ITask, mytask, 'MyTask')

When Zope is started, an event listener will start all tasks. 

  >>> from scheduler import manager
  >>> manager.startAllTasks(None)

  >>> mytask.running
  True
  >>> mytask.count
  0

At this time the first task execution should also be scheduled:

  >>> from twisted.internet import reactor
  >>> delayedCall = reactor.getDelayedCalls()[-1]

  >>> delayedCall.func
  MyTask(callable, *('arg1', 'arg2'), **{'kw1': 1, 'kw2': 2})

After the time passes (we just do not have time to wait 88 seconds ;-), the
task will be executed:

  >>> mytask()
  I have been called.

If you want to stop a task, then you simply call ``stop()``:

  >>> mytask.stop()
  >>> mytask.running
  False

For more documentation and information on a task's features, see Twisted's
``LoopingCall`` class, which is used as a base class for ``Task``.


Loop Task
---------

A looping task is a task that gets executed in evenly-spaced time
intervals. The interval can be specified in the final argument of the
constructor:

  >>> from scheduler import loop
  >>> looptask = loop.LoopTask(callable, interval=30)

The interval is specified in seconds, so in our case it is 30 seconds. The
time interval is publically available

  >>> looptask.timeInterval
  30

And when the delay is calculated, it should simply return the time interval:

  >>> looptask.computeDelayToNextCall()
  30


Cron Task
---------

The cron-based task allows descriptions of scheduled times via a crontab-like
format, where one can specify lists of minutes, hours, days, weekdays and
months. To properly test the calculation of the delay, we have to overridde
the time-module's ``time()`` function to return a constant time (in seconds).

  >>> import time
  >>> orig_time = time.time
  >>> time.time = lambda : time.mktime((2005, 1, 1, 0, 0, 0, 5, 1, 0))

We can now create a task.

  >>> from scheduler import cron
  >>> crontask = cron.CronTask(callable, (), {})
  
This corresponds to the crontab entry::

  * * * * * *

so that

  >>> time.localtime(crontask.computeDelayToNextCall())
  (2005, 1, 1, 0, 1, 0, 5, 1, 0)

Here are a couple more examples:

  # run five minutes after midnight, every day
  # 5 0 * * *
  >>> crontask = cron.CronTask(callable, (), {}, minute=(5,), hour=(0,))
  >>> time.localtime(crontask.computeDelayToNextCall())
  (2005, 1, 1, 0, 5, 0, 5, 1, 0)

  # run at 2:15pm on the first of every month
  # 15 14 1 * *
  >>> crontask = cron.CronTask(
  ...     callable, (), {}, 
  ...     minute=(5,), hour=(0,), dayOfMonth=(1,))
  >>> time.localtime(crontask.computeDelayToNextCall())
  (2005, 1, 1, 0, 5, 0, 5, 1, 0)

  # run at 10 pm on weekdays
  0 22 * * 1-5
  >>> crontask = cron.CronTask(
  ...     callable, (), {}, 
  ...     minute=(0,), hour=(22,), dayOfWeek=(1, 2, 3, 4, 5))
  >>> time.localtime(crontask.computeDelayToNextCall())
  (2005, 1, 1, 22, 0, 0, 5, 1, 0)

  # run 23 minutes after midn, 2am, 4am ..., everyday
  # 23 0-23/2 * * *
  >>> crontask = cron.CronTask(
  ...     callable, (), {}, minute=(23,), hour=xrange(0, 24, 2))
  >>> time.localtime(crontask.computeDelayToNextCall())
  (2005, 1, 1, 0, 23, 0, 5, 1, 0)

  # run at 5 after 4 every sunday
  5 4 * * sun
  >>> crontask = cron.CronTask(
  ...     callable, (), {}, 
  ...     minute=(5,), hour=(4,), dayOfWeek=(0,))
  >>> time.localtime(crontask.computeDelayToNextCall())
  (2005, 1, 3, 4, 5, 0, 0, 3, 0)


Finally, we need to cleanup after ourselves.

  >>> time.time = orig_time
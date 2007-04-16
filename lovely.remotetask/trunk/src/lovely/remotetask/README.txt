=====================
Remote Task Execution
=====================

This package provides an implementation of a remote task execution Web service
that allows to execute pre-defined tasks on another server. It is also
possible to run cron jobs at specific times. Those services are useful in two
ways:

1. They enable us to complete tasks that are not natively available on a
   particular machine. For example, it is not possible to convert an AVI file
   to a Flash(R) movie using Linux, the operating system our Web server might
   run on.

2. They also allow to move expensive operations to other servers. This is
   valuable, for example, when converting videos on high-traffic sites.

Let's now start by creating a single service:

  >>> from lovely import remotetask
  >>> service = remotetask.TaskService()

We can discover the available tasks:

  >>> service.getAvailableTasks()
  {}

This list is initially empty, because we have not registered any tasks. Let's
now define a task that simply echos an input string:

  >>> def echo(input):
  ...     return input

  >>> import lovely.remotetask.task
  >>> echoTask = remotetask.task.SimpleTask(echo)

The only API requirement on the converter is to be callable. Now we make sure
that the task works:

  >>> echoTask(service, 1, input={'foo': 'blah'})
  {'foo': 'blah'}

Let's now register the task as a utility:

  >>> import zope.component
  >>> zope.component.provideUtility(echoTask, name='echo')

The echo task is now available in the service:

  >>> service.getAvailableTasks()
  {u'echo': <SimpleTask <function echo ...>>}


Since the service cannot instantaneously complete a task, incoming jobs are
managed by a queue. First we request the echo task to be executed:

  >>> jobid = service.add(u'echo', {'foo': 'bar'})
  >>> jobid
  1

The ``add()`` function schedules the task called "echo" to be executed with
the specified arguments. The method returns a job id with which we can inquire
about the job.

  >>> service.getStatus(jobid)
  'queued'

Since the job has not been processed, the status is set to "queued". Further,
there is no result available yet:

  >>> service.getResult(jobid) is None
  True

As long as the job is not being processed, it can be cancelled:

  >>> service.cancel(jobid)
  >>> service.getStatus(jobid)
  'cancelled'

Let's now readd a job:

  >>> jobid = service.add(u'echo', {'foo': 'bar'})

The jobs in the queue are processed by calling the service's ``process()``
method:

  >>> service.process()

This method is usually called by other application logic, but we have to call
it manually here, since none of the other infrastructure is setup.

  >>> service.getStatus(jobid)
  'completed'
  >>> service.getResult(jobid)
  {'foo': 'bar'}

Now, let's define a new task that causes an error:

  >>> def error(input):
  ...     raise remotetask.task.TaskError('An error occurred.')

  >>> zope.component.provideUtility(
  ...     remotetask.task.SimpleTask(error), name='error')

Now add and execute it:

  >>> jobid = service.add(u'error')
  >>> service.process()

Let's now see what happened:

  >>> service.getStatus(jobid)
  'error'
  >>> service.getError(jobid)
  'An error occurred.'

For management purposes, the service also allows you to inspect all jobs:

  >>> dict(service.jobs)
  {1: <Job 1>, 2: <Job 2>, 3: <Job 3>}


To get rid of jobs not needed anymore one can use the clean method.

  >>> jobid = service.add(u'echo', {'blah': 'blah'})
  >>> sorted([job.status for job in service.jobs.values()])
  ['cancelled', 'completed', 'error', 'queued']
  
  >>> service.clean()

  >>> sorted([job.status for job in service.jobs.values()])
  ['queued']


Cron jobs
---------

Cron jobs execute on specific times.

  >>> import time
  >>> from lovely.remotetask.job import CronJob
  >>> now = 0
  >>> time.localtime(now)
  (1970, 1, 1, 1, 0, 0, 3, 1, 0)

We set up a job to be executed once an hour at the current minute. The next
call time is the one our from now.

Minutes

  >>> cronJob = CronJob(-1, u'echo', (), minute=(0, 10))
  >>> time.localtime(cronJob.timeOfNextCall(0))
  (1970, 1, 1, 1, 10, 0, 3, 1, 0)
  >>> time.localtime(cronJob.timeOfNextCall(10*60))
  (1970, 1, 1, 2, 0, 0, 3, 1, 0)

Hour

  >>> cronJob = CronJob(-1, u'echo', (), hour=(2, 13))
  >>> time.localtime(cronJob.timeOfNextCall(0))
  (1970, 1, 1, 2, 0, 0, 3, 1, 0)
  >>> time.localtime(cronJob.timeOfNextCall(2*60*60))
  (1970, 1, 1, 13, 0, 0, 3, 1, 0)

Month

  >>> cronJob = CronJob(-1, u'echo', (), month=(1, 5, 12))
  >>> time.localtime(cronJob.timeOfNextCall(0))
  (1970, 5, 1, 1, 0, 0, 4, 121, 0)
  >>> time.localtime(cronJob.timeOfNextCall(cronJob.timeOfNextCall(0)))
  (1970, 12, 1, 1, 0, 0, 1, 335, 0)

Day of week [0..6], jan 1 1970 is a wednesday.

  >>> cronJob = CronJob(-1, u'echo', (), dayOfWeek=(0, 2, 4, 5))
  >>> time.localtime(cronJob.timeOfNextCall(0))
  (1970, 1, 2, 1, 0, 0, 4, 2, 0)
  >>> time.localtime(cronJob.timeOfNextCall(60*60*24))
  (1970, 1, 3, 1, 0, 0, 5, 3, 0)
  >>> time.localtime(cronJob.timeOfNextCall(2*60*60*24))
  (1970, 1, 5, 1, 0, 0, 0, 5, 0)
  >>> time.localtime(cronJob.timeOfNextCall(4*60*60*24))
  (1970, 1, 7, 1, 0, 0, 2, 7, 0)

DayOfMonth [1..31]

  >>> cronJob = CronJob(-1, u'echo', (), dayOfMonth=(1, 12, 21, 30))
  >>> time.localtime(cronJob.timeOfNextCall(0))
  (1970, 1, 12, 1, 0, 0, 0, 12, 0)
  >>> time.localtime(cronJob.timeOfNextCall(12*24*60*60))
  (1970, 1, 21, 1, 0, 0, 2, 21, 0)

Combined

  >>> cronJob = CronJob(-1, u'echo', (), minute=(10,),
  ...                                 dayOfMonth=(1, 12, 21, 30))
  >>> time.localtime(cronJob.timeOfNextCall(0))
  (1970, 1, 1, 1, 10, 0, 3, 1, 0)
  >>> time.localtime(cronJob.timeOfNextCall(10*60))
  (1970, 1, 1, 2, 10, 0, 3, 1, 0)

  >>> cronJob = CronJob(-1, u'echo', (), minute=(10,),
  ...                                 hour=(4,),
  ...                                 dayOfMonth=(1, 12, 21, 30))
  >>> time.localtime(cronJob.timeOfNextCall(0))
  (1970, 1, 1, 4, 10, 0, 3, 1, 0)
  >>> time.localtime(cronJob.timeOfNextCall(10*60))
  (1970, 1, 1, 4, 10, 0, 3, 1, 0)


Creating Cron Jobs
------------------


  >>> count = 0
  >>> def counting(input):
  ...     global count
  ...     count += 1
  ...     return count
  >>> countingTask = remotetask.task.SimpleTask(counting)
  >>> zope.component.provideUtility(countingTask, name='counter')

here we create a cron job which runs 10 minutes and 13 minutes past the hour.

  >>> jobid = service.addCronJob(u'counter',
  ...                            {'foo': 'bar'},
  ...                            minute = (10, 13),
  ...                           )
  >>> service.getStatus(jobid)
  'cronjob'

We process the remote task but our cron job is not executed because we are too
early in time.

  >>> service.process(0)
  >>> service.getStatus(jobid)
  'cronjob'
  >>> service.getResult(jobid) is None
  True

Now we run the remote task 10 minutes later and get a result.

  >>> service.process(10*60)
  >>> service.getStatus(jobid)
  'cronjob'
  >>> service.getResult(jobid)
  1

And 1 minutes later it is not called.

  >>> service.process(11*60)
  >>> service.getResult(jobid)
  1

But 3 minutes later it is called again.

  >>> service.process(13*60)
  >>> service.getResult(jobid)
  2


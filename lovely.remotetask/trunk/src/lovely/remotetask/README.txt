=====================
Remote Task Execution
=====================

This package provides an implementation of a remote task execution Web service
that allows to execute pre-defined tasks on another server. Those services are
useful in two ways:

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

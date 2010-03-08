=====================
Remote Task Execution
=====================

.. contents::

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

Installation
------------

Define the remotetasks that should be started on startup in zope.conf like
this::

  <product-config lovely.remotetask>
    autostart site1@TestTaskService1, site2@TestTaskService2, @RootTaskService
  </product-config>

Note that services registered directly in the root folder can be referred to
by just prefixing them with the `@` symbol. The site name can be omitted. An
example of this is `RootTaskService` referenced above.

This causes the Remotetasks being started upon zope startup.

Usage
_____

  >>> STOP_SLEEP_TIME = 0.02

Let's now start by creating a single service:

  >>> from lovely import remotetask
  >>> service = remotetask.TaskService()

The object should be located, so it gets a name:

  >>> from zope.app.folder import Folder
  >>> site1 = Folder()
  >>> root['site1'] = site1
  >>> from zope.app.component.site import LocalSiteManager
  >>> from zope.security.proxy import removeSecurityProxy
  >>> sm = LocalSiteManager(removeSecurityProxy(site1))
  >>> site1.setSiteManager(sm)

  >>> sm['default']['testTaskService1'] = service
  >>> service = sm['default']['testTaskService1'] # caution! proxy
  >>> service.__name__
  u'testTaskService1'
  >>> service.__parent__ is sm['default']
  True

Let's register it under the name `TestTaskService1`:

  >>> from zope import component
  >>> from lovely.remotetask import interfaces
  >>> sm = site1.getSiteManager()
  >>> sm.registerUtility(service, interfaces.ITaskService,
  ...                          name='TestTaskService1')


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
  1392637175

The ``add()`` function schedules the task called "echo" to be executed with
the specified arguments. The method returns a job id with which we can inquire
about the job.
By default the ``add()`` function adds and starts the job ASAP. Sometimes we need
to have a jobid but not to start the job yet. See startlater.txt how.

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

The service isn't being started by default:

  >>> service.isProcessing()
  False

The ``TaskService`` is being started automatically - if specified in
``zope.conf`` - as soon as the ``IDatabaseOpenedEvent`` is fired. Let's
emulate the ``zope.conf`` settings:

  >>> class Config(object):
  ...     mapping = {}
  ...     def getSectionName(self):
  ...         return 'lovely.remotetask'
  >>> config = Config()
  >>> config.mapping['autostart'] = (
  ...     'site1@TestTaskService1, site2@TestTaskService2,@RootTaskService')
  >>> from zope.app.appsetup.product import setProductConfigurations
  >>> setProductConfigurations([config])
  >>> from lovely.remotetask.service import getAutostartServiceNames
  >>> getAutostartServiceNames()
  ['site1@TestTaskService1', 'site2@TestTaskService2', '@RootTaskService']

Note that `RootTaskService` is for a use-case where the service is directly
registered at the root. We test this use-case in a separate footnote so that
the flow of this document is not broken. [#1]_

To get a clean logging environment let's clear the logging stack:

  >>> log_info.clear()

On Zope startup the ``IDatabaseOpenedEvent`` is fired, and will call
the ``bootStrap()`` method:

  >>> from ZODB.tests import util
  >>> import transaction
  >>> db = util.DB()
  >>> from zope.app.publication.zopepublication import ZopePublication
  >>> conn = db.open()
  >>> conn.root()[ZopePublication.root_name] = root
  >>> transaction.commit()

Fire the event:

  >>> from zope.app.appsetup.interfaces import DatabaseOpenedWithRoot
  >>> from lovely.remotetask.service import bootStrapSubscriber
  >>> event = DatabaseOpenedWithRoot(db)
  >>> bootStrapSubscriber(event)

and voila - the service is processing:

  >>> service.isProcessing()
  True

Checking out the logging will prove the started service:

  >>> print log_info
  lovely.remotetask INFO
    handling event IStartRemoteTasksEvent
  lovely.remotetask INFO
    service TestTaskService1 on site site1 started
  lovely.remotetask ERROR
    site site2 not found
  lovely.remotetask INFO
    service RootTaskService on site root started

The verification for the jobs in the root-level service is done in another
footnote [#2]_

To deal with a lot of services in one sites it will be possible to use
asterisks (*) to start services. In case of using site@* means start all
services in that site:

But first stop all processing services:

  >>> service.stopProcessing()
  >>> service.isProcessing()
  False

  >>> root_service.stopProcessing()
  >>> root_service.isProcessing()
  False

  >>> import time
  >>> time.sleep(STOP_SLEEP_TIME)

And reset the logger:

  >>> log_info.clear()

Reset the product configuration with the asterisked service names:

  >>> config.mapping['autostart'] = 'site1@*'
  >>> setProductConfigurations([config])
  >>> getAutostartServiceNames()
  ['site1@*']

Firing the event again will start all services in the configured site:

  >>> bootStrapSubscriber(event)

  >>> service.isProcessing()
  True

  >>> root_service.isProcessing()
  False

Let's checkout the logging:

  >>> print log_info
  lovely.remotetask INFO
    handling event IStartRemoteTasksEvent
  lovely.remotetask INFO
    service TestTaskService1 on site site1 started

To deal with a lot of services in a lot of sites it possible to use
asterisks (*) to start services. In case of using *@* means start all
services on all sites:

  >>> service.stopProcessing()
  >>> service.isProcessing()
  False

  >>> import time
  >>> time.sleep(STOP_SLEEP_TIME)

Reset the product configuration with the asterisked service names:

  >>> config.mapping['autostart'] = '*@*'
  >>> setProductConfigurations([config])
  >>> getAutostartServiceNames()
  ['*@*']

...and reset the logger:

  >>> log_info.clear()

And fire the event again. All services should be started now:

  >>> bootStrapSubscriber(event)

  >>> service.isProcessing()
  True

  >>> root_service.isProcessing()
  True

Let's check the logging:

  >>> print log_info
  lovely.remotetask INFO
    handling event IStartRemoteTasksEvent
  lovely.remotetask INFO
    service RootTaskService on site root started
  lovely.remotetask INFO
    service TestTaskService1 on site site1 started


To deal with a specific service in a lot of sites it possible to use
asterisks (*) to start services. In case of using \*@service means start the
service called `service` on all sites:

  >>> service.stopProcessing()
  >>> service.isProcessing()
  False

  >>> root_service.stopProcessing()
  >>> root_service.isProcessing()
  False

  >>> import time
  >>> time.sleep(STOP_SLEEP_TIME)

Reset the product configuration with the asterisked service names:

  >>> config.mapping['autostart'] = '*@TestTaskService1'
  >>> setProductConfigurations([config])
  >>> getAutostartServiceNames()
  ['*@TestTaskService1']

...and reset the logger:

  >>> log_info.clear()

And fire the event again. All services should be started now:

  >>> bootStrapSubscriber(event)

  >>> service.isProcessing()
  True

  >>> root_service.isProcessing()
  False

Let's checkout the logging:

  >>> print log_info
  lovely.remotetask INFO
    handling event IStartRemoteTasksEvent
  lovely.remotetask INFO
    service TestTaskService1 on site site1 started

In case of configuring a directive which does not match any service on
any site logging will show a warning message:

  >>> service.stopProcessing()
  >>> service.isProcessing()
  False

  >>> import time
  >>> time.sleep(STOP_SLEEP_TIME)

  >>> config.mapping['autostart'] = '*@Foo'
  >>> setProductConfigurations([config])
  >>> getAutostartServiceNames()
  ['*@Foo']

  >>> log_info.clear()

  >>> bootStrapSubscriber(event)

  >>> service.isProcessing()
  False

  >>> root_service.isProcessing()
  False

  >>> print log_info
  lovely.remotetask INFO
    handling event IStartRemoteTasksEvent
  lovely.remotetask WARNING
    no services started by directive *@Foo

Finally stop processing and kill the thread. We'll call service.process()
manually as we don't have the right environment in the tests.

  >>> service.stopProcessing()
  >>> service.isProcessing()
  False

  >>> root_service.stopProcessing()
  >>> root_service.isProcessing()
  False

  >>> import time
  >>> time.sleep(STOP_SLEEP_TIME)

Let's now read a job:

  >>> jobid = service.add(u'echo', {'foo': 'bar'})
  >>> service.process()

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
  {1392637176: <Job 1392637176>, 1392637177: <Job 1392637177>, 1392637175: <Job 1392637175>}


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
  >>> time.gmtime(now)
  (1970, 1, 1, 0, 0, 0, 3, 1, 0)

We set up a job to be executed once an hour at the current minute. The next
call time is the one our from now.

Minutes

  >>> cronJob = CronJob(-1, u'echo', (), minute=(0, 10))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  (1970, 1, 1, 0, 10, 0, 3, 1, 0)
  >>> time.gmtime(cronJob.timeOfNextCall(10*60))
  (1970, 1, 1, 1, 0, 0, 3, 1, 0)

Hour

  >>> cronJob = CronJob(-1, u'echo', (), hour=(2, 13))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  (1970, 1, 1, 2, 0, 0, 3, 1, 0)
  >>> time.gmtime(cronJob.timeOfNextCall(2*60*60))
  (1970, 1, 1, 13, 0, 0, 3, 1, 0)

Month

  >>> cronJob = CronJob(-1, u'echo', (), month=(1, 5, 12))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  (1970, 5, 1, 0, 0, 0, 4, 121, 0)
  >>> time.gmtime(cronJob.timeOfNextCall(cronJob.timeOfNextCall(0)))
  (1970, 12, 1, 0, 0, 0, 1, 335, 0)

Day of week [0..6], jan 1 1970 is a wednesday.

  >>> cronJob = CronJob(-1, u'echo', (), dayOfWeek=(0, 2, 4, 5))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  (1970, 1, 2, 0, 0, 0, 4, 2, 0)
  >>> time.gmtime(cronJob.timeOfNextCall(60*60*24))
  (1970, 1, 3, 0, 0, 0, 5, 3, 0)
  >>> time.gmtime(cronJob.timeOfNextCall(2*60*60*24))
  (1970, 1, 5, 0, 0, 0, 0, 5, 0)
  >>> time.gmtime(cronJob.timeOfNextCall(4*60*60*24))
  (1970, 1, 7, 0, 0, 0, 2, 7, 0)

DayOfMonth [1..31]

  >>> cronJob = CronJob(-1, u'echo', (), dayOfMonth=(1, 12, 21, 30))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  (1970, 1, 12, 0, 0, 0, 0, 12, 0)
  >>> time.gmtime(cronJob.timeOfNextCall(12*24*60*60))
  (1970, 1, 21, 0, 0, 0, 2, 21, 0)

Combined

  >>> cronJob = CronJob(-1, u'echo', (), minute=(10,),
  ...                                 dayOfMonth=(1, 12, 21, 30))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  (1970, 1, 1, 0, 10, 0, 3, 1, 0)
  >>> time.gmtime(cronJob.timeOfNextCall(10*60))
  (1970, 1, 1, 1, 10, 0, 3, 1, 0)

  >>> cronJob = CronJob(-1, u'echo', (), minute=(10,),
  ...                                 hour=(4,),
  ...                                 dayOfMonth=(1, 12, 21, 30))
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  (1970, 1, 1, 4, 10, 0, 3, 1, 0)
  >>> time.gmtime(cronJob.timeOfNextCall(10*60))
  (1970, 1, 1, 4, 10, 0, 3, 1, 0)


A cron job can also be used to delay the execution of a job.

  >>> cronJob = CronJob(-1, u'echo', (), delay=10,)
  >>> time.gmtime(cronJob.timeOfNextCall(0))
  (1970, 1, 1, 0, 0, 10, 3, 1, 0)
  >>> time.gmtime(cronJob.timeOfNextCall(1))
  (1970, 1, 1, 0, 0, 11, 3, 1, 0)


Creating Delayed Jobs
---------------------

A delayed job is executed once after the given delay time in seconds.

  >>> count = 0
  >>> def counting(input):
  ...     global count
  ...     count += 1
  ...     return count
  >>> countingTask = remotetask.task.SimpleTask(counting)
  >>> zope.component.provideUtility(countingTask, name='counter')

  >>> jobid = service.addCronJob(u'counter',
  ...                            {'foo': 'bar'},
  ...                            delay = 10,
  ...                           )
  >>> service.getStatus(jobid)
  'delayed'
  >>> service.process(0)
  >>> service.getStatus(jobid)
  'delayed'
  >>> service.process(9)
  >>> service.getStatus(jobid)
  'delayed'

At 10 seconds the job is executed and completed.

  >>> service.process(10)
  >>> service.getStatus(jobid)
  'completed'


Creating Cron Jobs
------------------

Here we create a cron job which runs 10 minutes and 13 minutes past the hour.

  >>> count = 0

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

A job can be rescheduled.

  >>> job = service.jobs[jobid]
  >>> job.update(minute = (11, 13))

After the update the job must be rescheduled in the service.

  >>> service.reschedule(jobid)

Now the job is not executed at the old registration minute which was 10.

  >>> service.process(10*60+60*60)
  >>> service.getResult(jobid)
  2

But it executes at the new minute which is set to 11.

  >>> service.process(11*60+60*60)
  >>> service.getResult(jobid)
  3


Threading behavior
------------------

Each task service runs in a separate thread, allowing them to operate
independently.  Tasks should be designed to avoid conflict errors in
the database.

Let's start the task services we have defined at this point, and see
what threads are running as a result:

  >>> service.startProcessing()
  >>> root_service.startProcessing()

  >>> import pprint
  >>> import threading

  >>> def show_threads():
  ...     threads = [t for t in threading.enumerate()
  ...                if t.getName().startswith('remotetasks.')]
  ...     threads.sort(key=lambda t: t.getName())
  ...     pprint.pprint(threads)

  >>> show_threads()
  [<Thread(remotetasks.rootTaskService, started daemon)>,
   <Thread(remotetasks.site1.++etc++site.default.testTaskService1, started daemon)>]

Let's add a second site containing a task service with the same name as the
service in the first site:

  >>> site2 = Folder()
  >>> service2 = remotetask.TaskService()

  >>> root['site2'] = site2
  >>> sm = LocalSiteManager(removeSecurityProxy(site2))
  >>> site2.setSiteManager(sm)

  >>> sm['default']['testTaskService1'] = service2
  >>> service2 = sm['default']['testTaskService1'] # caution! proxy

Let's register it under the name `TestTaskService1`:

  >>> sm = site2.getSiteManager()
  >>> sm.registerUtility(
  ...     service2, interfaces.ITaskService, name='TestTaskService1')

The service requires that it's been committed to the database before it can
be used:

  >>> transaction.commit()

The new service isn't currently processing:

  >>> service2.isProcessing()
  False

If we start the new service, we can see that there are now three background
threads:

  >>> service2.startProcessing()
  >>> show_threads()
  [<Thread(remotetasks.rootTaskService, started daemon)>,
   <Thread(remotetasks.site1.++etc++site.default.testTaskService1, started daemon)>,
   <Thread(remotetasks.site2.++etc++site.default.testTaskService1, started daemon)>]

Let's stop the services, and give the background threads a chance to get the
message:

  >>> service.stopProcessing()
  >>> service2.stopProcessing()
  >>> root_service.stopProcessing()

  >>> import time
  >>> time.sleep(STOP_SLEEP_TIME)

The threads have exited now:

  >>> print [t for t in threading.enumerate()
  ...        if t.getName().startswith('remotetasks.')]
  []


Footnotes
---------

.. [#1] Tests for use-cases where a service is registered at `root` level.

   Register service for RootLevelTask

     >>> root_service = remotetask.TaskService()
     >>> component.provideUtility(root_service, interfaces.ITaskService,
     ...                          name='RootTaskService')

   The object should be located, so it get's a name:

     >>> root['rootTaskService'] = root_service
     >>> root_service = root['rootTaskService'] # caution! proxy
     >>> root_service.__name__
     u'rootTaskService'
     >>> root_service.__parent__ is root
     True

     >>> r_jobid = root_service.add(
     ...     u'echo', {'foo': 'this is for root_service'})
     >>> r_jobid
     1506179619


.. [#2] We verify the root_service does get processed:

     >>> root_service.isProcessing()
     True

   Cleaning up root-level service:

     >>> print root_service.getStatus(r_jobid)
     queued

   Thus the root-service is indeed enabled, which is what we wanted to verify.
   The rest of the API is tested in the main content above; so we don't need
   to test it again. We just clean up the the root service.

     >>> root_service.stopProcessing()
     >>> root_service.isProcessing()
     False

     >>> root_service.clean()


Check Interfaces and stuff
--------------------------

  >>> from zope.interface.verify import verifyClass, verifyObject
  >>> verifyClass(interfaces.ITaskService, remotetask.TaskService)
  True
  >>> verifyObject(interfaces.ITaskService, service)
  True
  >>> interfaces.ITaskService.providedBy(service)
  True

  >>> from lovely.remotetask.job import Job
  >>> fakejob = Job(1, u'echo', {})
  >>> verifyClass(interfaces.IJob, Job)
  True
  >>> verifyObject(interfaces.IJob, fakejob)
  True
  >>> interfaces.IJob.providedBy(fakejob)
  True

  >>> fakecronjob = CronJob(1, u'echo', {})
  >>> verifyClass(interfaces.ICronJob, CronJob)
  True
  >>> verifyObject(interfaces.ICronJob, fakecronjob)
  True
  >>> interfaces.IJob.providedBy(fakecronjob)
  True

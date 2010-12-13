==================================
Task Service Browser Management UI
==================================


  >>> from z3c.taskqueue.service import TaskService
  >>> service_instance = TaskService()

  >>> def echo(input):
  ...     return input

  >>> from z3c.taskqueue import task
  >>> echoTask = task.SimpleTask(echo)

  >>> echoTask(service_instance, 1, input={'foo': 'blah'})
  {'foo': 'blah'}

Let's now register the task as a utility:

  >>> import zope.component
  >>> zope.component.provideUtility(echoTask, name='echo')

The echo task is now available in the service:

  >>> service_instance.getAvailableTasks()
  {u'exception': <ExceptionTask>, u'echo': <SimpleTask <function echo ...>>}

Since the service cannot instantaneously complete a task, incoming jobs are
managed by a queue. First we request the echo task to be executed:

  >>> jobid = service_instance.add(u'echo', {'foo': 'bar'})
  >>> jobid
  1392637175

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

Let's instantiate a table to display the jobs...

  >>> from z3c.taskqueue_ui.browser import service
  >>> jobsTable = service.JobsTable(service_instance.jobs.values(), request)
  >>> jobsTable.update()

and render it.

  >>> table_html = jobsTable.render()
  >>> assert '<th>Task name</th>' in table_html
  >>> assert '<th>Status</th>' in table_html
  >>> assert '<th>Created</th>' in table_html
  >>> assert '<td>echo</td>' in table_html
  >>> assert '<td>queued</td>' in table_html

We can access an overview of the jobs in the service.

  >>> jobs_overview = service.JobsOverview(service_instance, request)
  >>> view_html = jobs_overview()

Let's check that it includes the table.

  >>> assert table_html in view_html

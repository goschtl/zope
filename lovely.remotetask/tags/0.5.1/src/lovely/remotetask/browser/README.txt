==================================
Task Service Browser Management UI
==================================

Let's start a browser:

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization','Basic mgr:mgrpw')
  >>> browser.handleErrors = False

Now we add a task service:

  >>> browser.open('http://localhost/manage')
  >>> browser.getLink('Remote Task Service').click()
  >>> browser.getControl(name='new_value').value = 'tasks'
  >>> browser.getControl('Apply').click()

Now let's have a look at the job's table:

  >>> browser.getLink('tasks').click()

You can see the available tasks:

  >>> 'Available Tasks' in browser.contents
  True

By default there is an "echo" task:

  >>> '<div>echo</div>' in browser.contents
  True

Below you see a table of all the jobs. Initially we have no jobs, so let's add
one via XML-RPC:

  >>> print http(r"""
  ... POST /tasks/ HTTP/1.0
  ... Authorization: Basic mgr:mgrpw
  ... Content-Type: text/xml
  ...
  ... <?xml version='1.0'?>
  ... <methodCall>
  ... <methodName>add</methodName>
  ... <params>
  ... <value><string>echo</string></value>
  ... <value><struct>
  ... <key><string>foo</string></key>
  ... <value><string>bar</string></value>
  ... </struct></value>
  ... </params>
  ... </methodCall>
  ... """)
  HTTP/1.0 200 Ok
  ...

If we now refresh the screen, we will see the new job:

  >>> browser.reload()
  >>> print browser.contents
  <!DOCTYPE ...
  <tbody>
  <tr class="odd">
    <td class="">
      <input type="checkbox" name="jobs:list" value="1506179619">
    </td>
    <td class="tableId">
      1506179619
    </td>
    <td class="tableTask">
      echo
    </td>
    <td class="tableStatus">
      <span class="status-queued">queued</span>
    </td>
    <td class="tableDetail">
      No input detail available
    </td>
    <td class="tableCreated">
      ...
    </td>
    <td class="tableStart">
      [not set]
    </td>
    <td class="tableEnd">
      [not set]
    </td>
  </tr>
  </tbody>
  ...

It is possible to provide custom views for the details. Note the name of the
view "echo_detail", it consists of the task name and "_detail". This allows us
to use different detail views on the same job classes. if no such view is
found a view with name 'detail' is searched.

  >>> from zope import interface
  >>> from zope.publisher.interfaces.browser import IBrowserView
  >>> class EchoDetailView(object):
  ...     interface.implements(IBrowserView)
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request
  ...     def __call__(self):
  ...         return u'echo: foo=%s'% self.context.input['foo']
  >>> from lovely.remotetask.interfaces import IJob
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope import component
  >>> component.provideAdapter(EchoDetailView,
  ...                          (IJob, IDefaultBrowserLayer),
  ...                          name='echo_detail')
  >>> browser.reload()
  >>> print browser.contents
  <!DOCTYPE
  ...
  <td class="tableDetail">
    echo: foo=bar
  ...

You can cancel scheduled jobs:

  >>> browser.getControl('Cancel', index=0).click()
  >>> 'No jobs were selected.' in browser.contents
  True

  >>> browser.getControl(name='jobs:list').getControl(
  ...     value='1506179619').click()
  >>> browser.getControl('Cancel', index=0).click()
  >>> 'Jobs were successfully cancelled.' in browser.contents
  True

It is also possible cancel all jobs::

  >>> browser.getControl('Cancel all', index=0).click()
  >>> 'All jobs cancelled' in browser.contents
  True

You can also clean attic jobs:

  >>> browser.getControl('Remove all').click()
  >>> 'Cleaned 1 Jobs' in  browser.contents
  True


Thread Exception Reporting
--------------------------

If a job raises an exception the task service repeats the job 3 times. On
every exception a traceback is written to the log.

We modify the python logger to get the log output.

  >>> import logging
  >>> logger = logging.getLogger("lovely.remotetask")
  >>> logger.setLevel(logging.ERROR)
  >>> import StringIO
  >>> io = StringIO.StringIO()
  >>> ch = logging.StreamHandler(io)
  >>> ch.setLevel(logging.DEBUG)
  >>> logger.addHandler(ch)

  >>> from time import sleep
  >>> from zope import component
  >>> from lovely.remotetask.interfaces import ITaskService
  >>> service = getRootFolder()['tasks']

We add a job for a task which raises a ZeroDivisionError every time it is
called.

  >>> jobid = service.add(u'exception')
  >>> service.getStatus(jobid)
  'queued'
  >>> import transaction
  >>> transaction.commit()
  >>> service.startProcessing()
  >>> transaction.commit()

  >>> import time
  >>> time.sleep(1.5)


Note that the processing thread is daemonic, that way it won't keep the process
alive unnecessarily.

  >>> import threading
  >>> for thread in threading.enumerate():
  ...     if thread.getName().startswith('remotetasks.'):
  ...         print thread.isDaemon()
  True

  >>> service.stopProcessing()
  >>> transaction.commit()


We got log entries with the tracebacks of the division error.

  >>> logvalue = io.getvalue()
  >>> print logvalue
  Caught a generic exception, preventing thread from crashing
  integer division or modulo by zero
  Traceback (most recent call last):
  ...
  ZeroDivisionError: integer division or modulo by zero
  <BLANKLINE>

We had 3 retries, but every error is reported twice, once by the processor and
once from by the task service.

  >>> logvalue.count('ZeroDivisionError')
  6

The job status is set to 'error'.

  >>> service.getStatus(jobid)
  'error'

We do the same again to see if the same thing happens again. This test is
necessary to see if the internal runCount in the task service is reset.

  >>> io.seek(0)
  >>> jobid = service.add(u'exception')
  >>> service.getStatus(jobid)
  'queued'
  >>> import transaction
  >>> transaction.commit()
  >>> service.startProcessing()
  >>> transaction.commit()
  >>> sleep(1.5)
  >>> service.stopProcessing()
  >>> transaction.commit()

We got log entries with the tracebacks of the division error.

  >>> logvalue = io.getvalue()
  >>> print logvalue
  Caught a generic exception, preventing thread from crashing
  integer division or modulo by zero
  Traceback (most recent call last):
  ...
  ZeroDivisionError: integer division or modulo by zero
  <BLANKLINE>

We had 3 retries, but every error is reported twice, once by the processor and
once from by the task service.

  >>> logvalue.count('ZeroDivisionError')
  6

The job status is set to 'error'.

  >>> service.getStatus(jobid)
  'error'


Clenaup
-------

Allow the threads to exit:

  >>> sleep(0.2)

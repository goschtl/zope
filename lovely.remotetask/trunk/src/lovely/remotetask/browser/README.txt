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
  <!DOCTYPE
  ...
  <tbody>
  <tr class="odd">
    <td class="">
      <input type="checkbox" name="jobs:list" value="1">
    </td>
    <td class="tableId">
      1
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

You can cancel scheduled jobs:

  >>> browser.getControl('Cancel').click()
  >>> 'No jobs were selected.' in browser.contents
  True

  >>> browser.getControl(name='jobs:list').getControl(value='1').click()
  >>> browser.getControl('Cancel').click()
  >>> 'Jobs were successfully cancelled.' in browser.contents
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

We add e job for a task which raises a ZeroDivisionError every time it is
called.

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
  catched a generic exception, preventing thread from crashing
  integer division or modulo by zero
  Traceback (most recent call last):
  ...
  ZeroDivisionError: integer division or modulo by zero
  <BLANKLINE>

We had 3 retries.

  >>> logvalue.count('ZeroDivisionError')
  3

The job status is set to 'error'.

  >>> service.getStatus(jobid)
  'error'

We do the same again to see if the same thin happens again. This test is
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
  catched a generic exception, preventing thread from crashing
  integer division or modulo by zero
  Traceback (most recent call last):
  ...
  ZeroDivisionError: integer division or modulo by zero
  <BLANKLINE>

We had 3 retries.

  >>> logvalue.count('ZeroDivisionError')
  3

The job status is set to 'error'.

  >>> service.getStatus(jobid)
  'error'


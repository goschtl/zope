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

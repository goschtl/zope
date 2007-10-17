=====================
Lovely Relations Demo
=====================

This demo creates a view document class which can be related to other
documents. All documents track their backreferences.

In our test setup the relations utility is already created and
registered. So we can start creating some objects.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization','Basic mgr:mgrpw')
  >>> browser.handleErrors=False
  >>> for i in range(1,4):
  ...     browser.open('http://localhost/@@contents.html')
  ...     browser.getLink('Related Document').click()
  ...     browser.getControl(name="new_value").value=u'doc%s' % i
  ...     browser.getControl('Apply').click()

Let us go to the edit form of the first document.

  >>> browser.open('http://localhost/doc1/manage')
  >>> browser.url
  'http://localhost/doc1/@@edit.html'

Note: We have a custom widget here, which lets us relate objects by
providing a comma-seperated list of names. The standard zope widget
uses javascript, so we can't test it with tesbrowser.

  >>> browser.getControl('Related').value
  ''
  >>> browser.getControl('Related').value = 'doc2, doc3'
  >>> browser.getControl('Change').click()

  >>> '<p>Updated on ' in browser.contents
  True

  >>> browser.open('http://localhost/doc1/@@edit.html')
  >>> browser.getControl('Related').value
  'doc2, doc3'

Change the order.

  >>> browser.getControl('Related').value = 'doc3, doc2'
  >>> browser.getControl('Change').click()
  >>> browser.open('http://localhost/doc1/@@edit.html')
  >>> browser.getControl('Related').value
  'doc3, doc2'

Let's have a look at the backrefs of doc2. This is a readonly
attribute, so a display widget is rendered.

  >>> browser.open('http://localhost/doc2/@@edit.html')
  >>> print browser.contents
  <...
  <div class="row">
      <div class="label">
        <label for="field.backrefs" title="">Backreferences</label>
      </div>
      <div class="field"><ul id="field.backrefs" ><li>doc1</li></ul></div>
  </div>...


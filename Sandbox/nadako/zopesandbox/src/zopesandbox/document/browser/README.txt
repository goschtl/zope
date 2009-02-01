Here we test simple add/edit/view workflow just like the user does that.

Let's create a test browser and load contents.html view for the root.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.open('http://localhost/@@contents.html')

Let's locate and click the "Document" link on the add menu.

  >>> browser.getLink('Document').click()

We should get an adding form:

  >>> browser.url
  'http://localhost/+/zopesandbox.Document='

  >>> print browser.contents
  <!DOCTYPE html PUBLIC...
  ...<input...id="field.title" name="field.title".../>...
  ...<textarea...id="field.description" name="field.description"...></textarea>...
  ...<textarea...id="field.body" name="field.body"...></textarea>...

Let's fill and click the "Add" button.

  >>> browser.getControl('Title').value = u'Main page'
  >>> browser.getControl('Description').value = u'This is a site root'
  >>> browser.getControl('Body text').value = u'<h2>Welcome</h2>'
  >>> browser.getControl(name='add_input_name').value = 'front-page'
  >>> browser.getControl('Add').click()

Now, our new document, named "front-page" is listed in contents.html.

  >>> browser.url
  'http://localhost/@@contents.html'
 
  >>> 'front-page' in browser.contents
  True

We get the edit form when clicking on the object's name:

  >>> browser.getLink('front-page').click()
  >>> browser.url
  'http://localhost/front-page/@@edit.html'
 
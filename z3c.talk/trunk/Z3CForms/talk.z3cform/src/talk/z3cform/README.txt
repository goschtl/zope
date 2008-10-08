=======================
The Hello World Message
=======================

This package implements the forms for the Hello World Message content
component.

Create a browser instance:

  >>> from zope.testbrowser.testing import Browser
  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> manager.addHeader('Accept-Language', 'en')

Let's create a message component first:

  >>> manager.handleErrors = False
  >>> manager.open('http://localhost:8080/++skin++Form/addHelloWorld.html')

  >>> manager.getControl('Who').value = u'Stephan'
  >>> manager.getControl('When').value = u'1/1/07'
  >>> manager.getControl('What').getControl('sunny').click()

  >>> manager.getControl('Add').click()

We should be forwarded to the message's display screen:

  >>> print manager.contents
  <html>
    <body>
      <h1>
        A <span id="form-widgets-what"
        class="select-widget required choice-field"><span
      class="selected-option">sunny</span></span>
   Hello World
        from <span id="form-widgets-who"
        class="text-widget required textline-field">Stephan</span>
  <BLANKLINE>
        on <span id="form-widgets-when"
        class="text-widget required date-field">1/1/07</span>
  !
      </h1>
      <a href="http://localhost:8080/++skin++Form/helloworld-0/edit.html">
        Edit Message</a>
    </body>
  </html>


You can click the edit button to change the data:

  >>> manager.getLink('Edit Message').click()

  >>> manager.getControl('Who').value = u'Roger'
  >>> manager.getControl('When').value = u'1/2/07'
  >>> manager.getControl('What').getControl('best').click()

  >>> manager.getControl('Apply and View').click()

This action forwards you again to the view page:

  >>> print manager.contents
  <html>
    <body>
      <h1>
        A <span id="form-widgets-what"
        class="select-widget required choice-field"><span
      class="selected-option">best</span></span>
   Hello World
        from <span id="form-widgets-who"
        class="text-widget required textline-field">Roger</span>
  <BLANKLINE>
        on <span id="form-widgets-when"
        class="text-widget required date-field">1/2/07</span>
  !
      </h1>
      <a href="http://localhost:8080/++skin++Form/helloworld-0/edit.html">
        Edit Message</a>
    </body>
  </html>

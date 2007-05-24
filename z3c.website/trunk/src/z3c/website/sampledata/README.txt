======================
Sample Data Generation
======================

Setup the test browser and go to the sampledata.html page.

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = False


Setup z3c.website
-----------------

  >>> browser.open('http://localhost/@@managesamples.html')
  >>> browser.getLink(text='z3c.website.site').click()
  >>> browser.url
  'http://localhost/@@generatesample.html?manager=z3c.website'

Now we fill in the form and generate the sample site.

  >>> browser.getControl(name='generator.seed').value = 'sample'
  >>> browser.getControl(name='z3c.website.site.__name__').value = 'xpo'
  >>> browser.getControl(name='z3c.website.site.title').value = 'Z3C'
  >>> browser.getControl('Generate').click()

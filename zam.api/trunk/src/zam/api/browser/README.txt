======
README
======

This package contains the Zope Application Management api. We support a test
skin for this package which allows us to test the plugin management page.
There is also a ZAMTest site available whcih this test will use. This test site
can also be used in any other zam.* or zamplugin.* package.

Login as manager first:

  >>> from zope.testbrowser.testing import Browser
  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')

Check if we can access the page.html view which is registred in the
ftesting.zcml file with our skin:

  >>> manager = Browser()
  >>> manager.handleErrors = False
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> skinURL = 'http://localhost/++skin++ZAMTest/index.html'
  >>> manager.open(skinURL)
  >>> manager.url
  'http://localhost/++skin++ZAMTest/index.html'

Now let's create a test site called ``first`` and add them to the root:

  >>> import zam.api.testing
  >>> root = getRootFolder()
  >>> firstSite = zam.api.testing.ZAMTestSite(u'first')
  >>> root['first'] = firstSite

And create another one called ``second``:

  >>> secondSite = zam.api.testing.ZAMTestSite(u'second')
  >>> root['second'] = secondSite

Go the the new zam test site:

  >>> firstSiteURL = 'http://localhost/++skin++ZAMTest/first'
  >>> manager.open(firstSiteURL + '/index.html')
  >>> manager.url
  'http://localhost/++skin++ZAMTest/first/index.html'

and to the ``second`` site:

  >>> secondSiteURL = 'http://localhost/++skin++ZAMTest/second'
  >>> manager.open(secondSiteURL + '/index.html')
  >>> manager.url
  'http://localhost/++skin++ZAMTest/second/index.html'

and go to the ``plugins.html`` page:

  >>> manager.open(firstSiteURL + '/plugins.html')

Now we see the plugins.html page:

  >>> print manager.contents
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
        lang="en">
  <head>
  <title>ZAM</title><meta http-equiv="cache-control" content="no-cache" />
  <meta http-equiv="pragma" content="no-cache" />
  </head>
  <body>
  <form action="http://localhost/++skin++ZAMTest/first/plugins.html"
        method="post" enctype="multipart/form-data"
        class="edit-form" name="form" id="form">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>
           &ndash; required
        </div>
      <div>
    <h1>ZAM Plugin Management</h1>
    <fieldset>
      <legend>
        ZAM test plugin&nbsp;
      (not installed)
    </legend>
    <br />
    <div><p>ZAM test plugin.</p>
  </div>
    <br />
    <span>install</span>
    <input type="radio" class="radio-widget"
           name="zam.api.testing" value="install">
    <span>uninstall</span>
    <input type="radio" class="radio-widget"
           name="zam.api.testing" value="uninstall"
           checked="checked">
     </fieldset>
    </div>
    </div>
    <div>
      <div class="buttons">
        <input type="submit" id="form-buttons-apply"
               name="form.buttons.apply"
               class="submit-widget button-field" value="Apply" />
      </div>
    </div>
  </form>
  </body>
  </html>

Before we install the plugin, we try to access the page which only is available
if the zam test plugin is installed:

  >>> manager.open(firstSiteURL + '/test.html')
  Traceback (most recent call last):
  ...
  NotFound: Object: <ZAMTestSite u'first'>, name: u'test.html'

The ``second`` site does also not provide such a test page:

  >>> manager.open(secondSiteURL + '/test.html')
  Traceback (most recent call last):
  ...
  NotFound: Object: <ZAMTestSite u'second'>, name: u'test.html'

As you can see there is no such ``test.html`` page. Let's install our zam test
plugin:

  >>> manager.open(firstSiteURL + '/plugins.html')
  >>> manager.getControl(name='zam.api.testing').value = ['install']
  >>> manager.getControl('Apply').click()

Now we can see that the plugin is installed:

  >>> print manager.contents
  <!DOCTYPE...
   <input type="radio" class="radio-widget"
         name="zam.api.testing" value="install"
         checked="checked">
  ...
   <input type="radio" class="radio-widget"
         name="zam.api.testing" value="uninstall">
  ...

Now make test coverage happy and test to install a alreay installed
plugin:

  >>> manager.open(firstSiteURL + '/plugins.html')
  >>> manager.getControl(name='zam.api.testing').value = ['install']
  >>> manager.getControl('Apply').click()

And the zam plugin test page is available at the ``first`` site

  >>> manager.open(firstSiteURL + '/test.html')
  >>> manager.url
  'http://localhost/++skin++ZAMTest/first/test.html'

But not at the ``second`` site:

  >>> manager.open(secondSiteURL + '/test.html')
  Traceback (most recent call last):
  ...
  NotFound: Object: <ZAMTestSite u'second'>, name: u'test.html'

Let's unsinstall the plugin:

  >>> manager.open(firstSiteURL + '/plugins.html')
  >>> manager.getControl(name='zam.api.testing').value = ['uninstall']
  >>> manager.getControl('Apply').click()

And check if the site is not available anymore:

  >>> manager.open(firstSiteURL + '/test.html')
  Traceback (most recent call last):
  ...
  NotFound: Object: <ZAMTestSite u'first'>, name: u'test.html'

Now make test coverage happy and test to uninstall a alreay uninstalled
plugin:

  >>> manager.open(firstSiteURL + '/plugins.html')
  >>> manager.getControl(name='zam.api.testing').value = ['uninstall']
  >>> manager.getControl('Apply').click()

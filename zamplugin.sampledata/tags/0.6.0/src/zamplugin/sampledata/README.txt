======
README
======

This package provides sampledata pages for the z3c.sampledata implementation. 
The zam.skin is used as basic skin for this test.

First login as manager:

  >>> from zope.testbrowser.testing import Browser
  >>> mgr = Browser()
  >>> mgr.addHeader('Authorization', 'Basic mgr:mgrpw')

And go to the plugins page at the site root:

  >>> rootURL = 'http://localhost/++skin++ZAM'
  >>> mgr.open(rootURL + '/plugins.html')
  >>> mgr.url
  'http://localhost/++skin++ZAM/plugins.html'

and install the error plugins:

  >>> mgr.getControl(name='zamplugin.sampledata.buttons.install').click()
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
    <h1>ZAM Plugin Management</h1>
    <fieldset id="pluginManagement">
      <strong class="installedPlugin">Sample data configuration views</strong>
      <div class="description">ZAM sample data configuration views utility.</div>
  ...

Now you can see that we can access the error utility at the site root:

  >>> mgr.open(rootURL + '/sampledata.html')
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
  <div id="content">
    <h1>Sample Data Generation</h1>
    <div class="row">Select the sample manager</div>
      </div>
    </div>
  </div>
  ...

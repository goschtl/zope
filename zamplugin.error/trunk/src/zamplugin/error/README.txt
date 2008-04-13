======
README
======

This package provides the error utility pages. The zam.skin is used as basic 
skin for this test.

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

  >>> mgr.getControl(name='zamplugin.error.buttons.install').click()
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
    <h1>ZAM Plugin Management</h1>
    <fieldset id="pluginManagement">
      <strong class="installedPlugin">Error reporting utility</strong>
      <div class="description">ZAM Error reporting utility.</div>
  ...

Now you can see that we can access the error utility at the site root:

  >>> mgr.open(rootURL + '/++etc++site/default/RootErrorReportingUtility')
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
  <div id="content">
    <div>
    <h3>Exception Log (most recent first)</h3>
    <p>This page lists the exceptions that have occurred in this
      site recently.</p>
    <div>
      <em> No exceptions logged. </em>
  <BLANKLINE>
    </div>
    <!-- just offer reload button -->
    <form action="." method="get">
      <div class="row">
        <div class="controls">
          <input type="submit" name="submit" value="Refresh" />
        </div>
      </div>
    </form>
  </div>
  ...

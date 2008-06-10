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

Let's go to the edit.html page:

  >>> mgr.open(rootURL + '/++etc++site/default/RootErrorReportingUtility/edit.html')
  >>> print mgr.contents
  <!DOCTYPE ...
  ...<div class="widget"><input type="text" id="form-widgets-keep_entries"
                     name="form.widgets.keep_entries"
                     class="text-widget required int-field" value="20" />
  ...<label for="form-widgets-copy_to_zlog-1">
      <input type="radio" id="form-widgets-copy_to_zlog-1"
             name="form.widgets.copy_to_zlog:list"
             class="radio-widget required bool-field"
             value="false" checked="checked" />
      <span class="label">no</span>
  ...<div class="widget"><textarea id="form-widgets-ignored_exceptions"
            name="form.widgets.ignored_exceptions"
            class="textarea-widget required tuple-field">Unauthorized</textarea>
  ...

And change the configuration:

  >>> mgr.getControl('Keep entries').value = '10'
  >>> mgr.getControl(name='form.widgets.copy_to_zlog:list').value = ['true']
  >>> mgr.getControl('Ignore exceptions').value = 'UserError'
  >>> mgr.getControl('Apply').click()

Now go to the edit.html page and check the values again.

  >>> mgr.open(rootURL + '/++etc++site/default/RootErrorReportingUtility/edit.html')
  >>> print mgr.contents
  <!DOCTYPE ...
  ...<div class="widget"><input type="text" id="form-widgets-keep_entries"
                     name="form.widgets.keep_entries"
                     class="text-widget required int-field" value="10" />
  ...<label for="form-widgets-copy_to_zlog-1">
      <input type="radio" id="form-widgets-copy_to_zlog-1"
             name="form.widgets.copy_to_zlog:list"
             class="radio-widget required bool-field"
             value="false" />
      <span class="label">no</span>
  ...<div class="widget"><textarea id="form-widgets-ignored_exceptions"
            name="form.widgets.ignored_exceptions"
            class="textarea-widget required tuple-field">UserError</textarea>
  ...

======
README
======

This package provides the server control management. The zam.skin is used as
basic skin for this test.

First login as manager:

  >>> from zope.testbrowser.testing import Browser
  >>> mgr = Browser()
  >>> mgr.addHeader('Authorization', 'Basic mgr:mgrpw')

Check if we can access the management namespace without the installed plugin:

  >>> rootURL = 'http://localhost/++skin++ZAM'
  >>> mgr.open(rootURL + '/++etc++ApplicationController')
  Traceback (most recent call last):
  HTTPError: HTTP Error 404: Not Found

As you can see there is no real page available only the default one from the
skin configuration which shows the following message:

  >>> 'The page you are trying to access is not available' in mgr.contents
  True

Go to the plugins page at the site root:

  >>> mgr.open(rootURL + '/plugins.html')
  >>> mgr.url
  'http://localhost/++skin++ZAM/plugins.html'

and install the contents plugins:

  >>> mgr.getControl(name='zamplugin.control.buttons.install').click()
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
  <div id="content">
        <form action="./plugins.html" method="post" enctype="multipart/form-data" class="plugin-form">
    <h1>ZAM Plugin Management</h1>
    <fieldset id="pluginManagement">
      <strong class="installedPlugin">Server control plugin</strong>
      <div class="description">ZAM Control plugin.</div>
  ...

Now you can see there is management namespace at the site root:

  >>> mgr.open(rootURL + '/++etc++ApplicationController')
  >>> print mgr.contents
  <!DOCTYPE ...
   ...
   <div id="content">
     <div class="row">
       <div class="label">Uptime</div>
       ...
     </div>
     <div class="row">
       <div class="label">System platform</div>
       ...
     </div>
     <div class="row">
       <div class="label">Zope version</div>
       ...
     </div>
     <div class="row">
       <div class="label">Python version</div>
       ...
     </div>
     <div class="row">
       <div class="label">Command line</div>
       ...
     <div class="row">
       <div class="label">Preferred encoding</div>
       ...
     </div>
     <div class="row">
       <div class="label">FileSystem encoding</div>
       ...
     </div>
     <div class="row">
       <div class="label">Process id</div>
       ...
     </div>
     <div class="row">
       <div class="label">Developer mode</div>
       <div class="field">On</div>
     </div>
     <div class="row">
       <div class="label">Python path</div>
       ...
       </div>
     </div>
      </div>
    </div>
  </div>
  </body>
  </html>


The ZODB control page allows you to pack the Database and shows the current
database size:

  >>> mgr.open(rootURL + '/++etc++ApplicationController/ZODBControl.html')
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
  <div>
    <form action="http://localhost/++skin++ZAM/++etc++ApplicationController/ZODBControl.html"
          method="post">
    <div class="row">
      <table border="1">
          <tr>
            <th>Pack</th>
            <th>Utility Name</th>
            <th>Database Name</th>
            <th>Size</th>
          </tr>
          <tr>
            <td>
              <input type="checkbox" name="dbs:list"
                     value="unnamed" />
            </td>
            <td>
              unnamed
            </td>
            <td>
              Demo storage 'unnamed'
            </td>
            <td>
              2 KB
            </td>
          </tr>
      </table>
      <div class="row">
        <span class="label">Keep up to</span>
        <span class="field">
          <input type="text" size="4" name="days" value="0" />
          days
        </span>
        <div class="controls">
          <input type="submit" name="PACK" value="Pack" />
        </div>
      </div>
    </div>
    </form>
  </div>
  ...

The generation page shows you pending generations and will list already
processed generation steps:

  >>> mgr.open(rootURL + '/++etc++ApplicationController/generations.html')
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
  <div id="content">
    <span>Database generations</span>
  <form action="http://localhost/++skin++ZAM/++etc++ApplicationController/generations.html">
  <table border="1">
  <tr>
      <th>Application</th>
      <th>Minimum Generation</th>
      <th>Maximum Generation</th>
      <th>Current Database Generation</th>
      <th>Evolve?</th>
  </tr>
  <tr>
      <td>
        <a href="generationDetails.html?id=zope.app">zope.app</a>
      </td>
      <td>1</td>
      <td>5</td>
      <td>5</td>
      <td>
         <span>No, up to date</span>
      </td>
  </tr>
  </table>
  </form>
  ...

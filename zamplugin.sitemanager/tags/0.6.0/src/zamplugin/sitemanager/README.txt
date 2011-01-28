======
README
======

This package contains the site manager part for the Zope Application
Management. The zam.skin is used as basic skin for this test.

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

  >>> mgr.getControl(name='zamplugin.sitemanager.buttons.install').click()
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
    <h1>ZAM Plugin Management</h1>
    <fieldset id="pluginManagement">
      <strong class="installedPlugin">Site management</strong>
      <div class="description">ZAM Site Manager.</div>
  ...

Now you can see that we can access the contents.html page for our site
management container at the site root:

  >>> mgr.open(rootURL + '/++etc++site/default/@@contents.html')
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
      <div id="content">
        <form action="http://localhost/++skin++ZAM/++etc++site/default/@@contents.html"
        method="post" enctype="multipart/form-data"
        class="edit-form" name="contents" id="contents">
    <div class="viewspace">
      <div>
      <fieldset>
        <legend>Search</legend>
          <table>
  <tr>
  <td class="row">
    <label for="search-widgets-searchterm">Search</label>
      <input id="search-widgets-searchterm"
             name="search.widgets.searchterm"
             class="text-widget required textline-field"
             value="" type="text" />
  </td>
  <td class="action">
  <input id="search-buttons-search"
         name="search.buttons.search"
         class="submit-widget button-field" value="Search"
         type="submit" />
  </td>
  </tr>
  </table>
      </fieldset>
      <table class="contents">
    <thead>
      <tr>
        <th>X</th>
        <th><a href="?contents-sortOn=contents-renameColumn-1&contents-sortOrder=descending" title="Sort">Name</a></th>
        <th><a href="?contents-sortOn=contents-createdColumn-2&contents-sortOrder=ascending" title="Sort">Created</a></th>
        <th><a href="?contents-sortOn=contents-modifiedColumn-3&contents-sortOrder=ascending" title="Sort">Modified</a></th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="CookieClientIdManager"  /></td>
        <td><a href="http://localhost/++skin++ZAM/++etc++site/default/CookieClientIdManager">CookieClientIdManager</a></td>
        <td>None</td>
        <td>None</td>
      </tr>
      <tr class="odd">
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="PersistentSessionDataContainer"  /></td>
        <td><a href="http://localhost/++skin++ZAM/++etc++site/default/PersistentSessionDataContainer">PersistentSessionDataContainer</a></td>
        <td>None</td>
        <td>None</td>
      </tr>
      <tr class="even">
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="PrincipalAnnotation"  /></td>
        <td><a href="http://localhost/++skin++ZAM/++etc++site/default/PrincipalAnnotation">PrincipalAnnotation</a></td>
        <td>None</td>
        <td>None</td>
      </tr>
      <tr class="odd">
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="RootErrorReportingUtility"  /></td>
        <td><a href="http://localhost/++skin++ZAM/++etc++site/default/RootErrorReportingUtility">RootErrorReportingUtility</a></td>
        <td>None</td>
        <td>None</td>
      </tr>
    </tbody>
  </table>
    </div>
    </div>
    <div>
      <div class="buttons">
  <input id="contents-buttons-copy"
         name="contents.buttons.copy"
         class="submit-widget button-field" value="Copy"
         type="submit" />
  <input id="contents-buttons-cut" name="contents.buttons.cut"
         class="submit-widget button-field" value="Cut"
         type="submit" />
  <input id="contents-buttons-delete"
         name="contents.buttons.delete"
         class="submit-widget button-field" value="Delete"
         type="submit" />
  <input id="contents-buttons-rename"
         name="contents.buttons.rename"
         class="submit-widget button-field" value="Rename"
         type="submit" />
      </div>
    </div>
  </form>
  ...

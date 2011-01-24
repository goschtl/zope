======
README
======

This package contains a container managment view for the Zope Application 
Management.

Login as mgr first:

  >>> from zope.testbrowser.testing import Browser
  >>> mgr = Browser()
  >>> mgr.addHeader('Authorization', 'Basic mgr:mgrpw')

Check if we can access the index.html view which is registred within the ZAM 
skin:

  >>> mgr = Browser()
  >>> mgr.handleErrors = False
  >>> mgr.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> rootURL = 'http://localhost/++skin++ZAM'
  >>> mgr.open(rootURL + '/index.html')
  >>> mgr.url
  'http://localhost/++skin++ZAM/index.html'

  >>> 'There is no index.html page registered for this object' in  mgr.contents
  True

As you can see there is no real ``contents.hml`` page available only the default
one from the skin configuration which shows the following message:

  >>> mgr.open(rootURL + '/contents.html')
  >>> 'There is no contents.html page registered for this object' in mgr.contents
  True

Go to the plugins page at the site root:

  >>> mgr.open(rootURL + '/plugins.html')
  >>> mgr.url
  'http://localhost/++skin++ZAM/plugins.html'

and install the contents plugins:

  >>> mgr.getControl(name='zamplugin.contents.buttons.install').click()
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
  <h1>ZAM Plugin Management</h1>
   <fieldset id="pluginManagement">
     <strong class="installedPlugin">Container management page</strong>
     <div class="description">This container management page is configured for IReadContainer.</div>
  ...

Now you can see there is ``contents.html`` page at the site root:

  >>> mgr.open(rootURL + '/contents.html')
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
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
    </tbody>
  </table>
    </div>
    </div>
    <div>
      <div class="buttons">
      </div>
    </div>
  </form>
      </div>
    </div>
  </div>
  ...

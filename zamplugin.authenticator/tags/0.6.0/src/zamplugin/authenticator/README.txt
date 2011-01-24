======
README
======

This package provides management pages for the z3c.authenticator implementation. 
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

  >>> mgr.getControl(name='zamplugin.authenticator.buttons.install').click()
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
  <h1>ZAM Plugin Management</h1>
    <fieldset id="pluginManagement">
      <strong class="installedPlugin">Z3C Authenticator management</strong>
      <div class="description">ZAM Authenticator Management.</div>
  ...

Let's add and setup an Authenticator utility:

  >>> from zope.app.security.interfaces import IAuthentication
  >>> from z3c.authenticator.authentication import Authenticator
  >>> root = getRootFolder()
  >>> sm = root.getSiteManager()
  >>> auth = Authenticator()
  >>> sm['auth'] = auth
  >>> sm.registerUtility(auth, IAuthentication)

Now you can see that we can access the authenticator utility at the site root:

  >>> mgr.open(rootURL + '/++etc++site/auth/contents.html')
  >>> print mgr.contents
  <!DOCTYPE ...
  ...
  <ul>
    <li class="selected">
    <a href="http://localhost/++skin++ZAM/++etc++site/auth/contents.html"><span>Contents</span></a>
  ...
  ...
  <table>
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
   ...

The management page can be found at the edit.html page:

  >>> mgr.handleErrors = False
  >>> mgr.open(rootURL + '/++etc++site/auth/edit.html')
  >>> print mgr.contents
  <!DOCTYPE ...
      <div id="content">
        <form action="http://localhost/++skin++ZAM/++etc++site/auth/edit.html"
        method="post" enctype="multipart/form-data"
        class="edit-form" name="form" id="form">
    <div class="viewspace">
        <h1>Edit Authenticator.</h1>
        <div class="required-info">
           <span class="required">*</span>&ndash; required
        </div>
      <div>
            <div id="form-widgets-includeNextUtilityForAuthenticate-row"
                 class="row">
                <div class="label">
                  <label for="form-widgets-includeNextUtilityForAuthenticate">
                    <span>Include next utility for authenticate</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
  <span class="option">
    <label for="form-widgets-includeNextUtilityForAuthenticate-0">
      <input id="form-widgets-includeNextUtilityForAuthenticate-0"
             name="form.widgets.includeNextUtilityForAuthenticate:list"
             class="radio-widget required bool-field"
             value="true" checked="checked" type="radio" />
      <span class="label">yes</span>
    </label>
  </span>
  <span class="option">
    <label for="form-widgets-includeNextUtilityForAuthenticate-1">
      <input id="form-widgets-includeNextUtilityForAuthenticate-1"
             name="form.widgets.includeNextUtilityForAuthenticate:list"
             class="radio-widget required bool-field"
             value="false" type="radio" />
      <span class="label">no</span>
    </label>
  </span>
  <input name="form.widgets.includeNextUtilityForAuthenticate-empty-marker"
         type="hidden" value="1" />
  </div>
            </div>
            <div id="form-widgets-credentialsPlugins-row"
                 class="row">
                <div class="label">
                  <label for="form-widgets-credentialsPlugins">
                    <span>Credentials Plugins</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
  <script type="text/javascript">
  /*  <![CDATA[ */
  function moveItems(from, to)
    {
    // shortcuts for selection fields
    var src = document.getElementById(from);
    var tgt = document.getElementById(to);
    if (src.selectedIndex == -1) selectionError();
    else
      {
      // iterate over all selected items
      // --> attribute "selectedIndex" doesn't support multiple selection.
      // Anyway, it works here, as a moved item isn't selected anymore,
      // thus "selectedIndex" indicating the "next" selected item :)
      while (src.selectedIndex > -1)
        if (src.options[src.selectedIndex].selected)
          {
          // create a new virtal object with values of item to copy
          temp = new Option(src.options[src.selectedIndex].text,
                        src.options[src.selectedIndex].value);
          // append virtual object to targe
          tgt.options[tgt.length] = temp;
          // want to select newly created item
          temp.selected = true;
          // delete moved item in source
          src.options[src.selectedIndex] = null;
        }
      }
    }
  // move item from "from" selection to "to" selection
  function from2to(name)
    {
    moveItems(name+"-from", name+"-to");
    copyDataForSubmit(name);
    }
  // move item from "to" selection back to "from" selection
  function to2from(name)
    {
    moveItems(name+"-to", name+"-from");
    copyDataForSubmit(name);
    }
  function swapFields(a, b)
    {
    // swap text
    var temp = a.text;
    a.text = b.text;
    b.text = temp;
    // swap value
    temp = a.value;
    a.value = b.value;
    b.value = temp;
    // swap selection
    temp = a.selected;
    a.selected = b.selected;
    b.selected = temp;
    }
  // move selected item in "to" selection one up
  function moveUp(name)
    {
    // shortcuts for selection field
    var toSel = document.getElementById(name+"-to");
    if (toSel.selectedIndex == -1)
        selectionError();
    else if (toSel.options[0].selected)
        alert("Cannot move further up!");
    else for (var i = 0; i < toSel.length; i++)
      if (toSel.options[i].selected)
        {
        swapFields(toSel.options[i-1], toSel.options[i]);
        copyDataForSubmit(name);
        }
    }
  // move selected item in "to" selection one down
  function moveDown(name)
    {
      // shortcuts for selection field
      var toSel = document.getElementById(name+"-to");
      if (toSel.selectedIndex == -1) {
          selectionError();
      } else if (toSel.options[toSel.length-1].selected) {
          alert("Cannot move further down!");
      } else {
        for (var i = toSel.length-1; i >= 0; i--) {
          if (toSel.options[i].selected) {
            swapFields(toSel.options[i+1], toSel.options[i]);
          }
        }
        copyDataForSubmit(name);
      }
    }
  // copy each item of "toSel" into one hidden input field
  function copyDataForSubmit(name)
    {
    // shortcuts for selection field and hidden data field
    var toSel = document.getElementById(name+"-to");
    var toDataContainer = document.getElementById(name+"-toDataContainer");
    // delete all child nodes (--> complete content) of "toDataContainer" span
    while (toDataContainer.hasChildNodes())
        toDataContainer.removeChild(toDataContainer.firstChild);
    // create new hidden input fields - one for each selection item of
    // "to" selection
    for (var i = 0; i < toSel.options.length; i++)
      {
      // create virtual node with suitable attributes
      var newNode = document.createElement("input");
      var newAttr = document.createAttribute("name");
      newAttr.nodeValue = name.replace(/-/g, '.')+':list';
      newNode.setAttributeNode(newAttr);
      newAttr = document.createAttribute("type");
      newAttr.nodeValue = "hidden";
      newNode.setAttributeNode(newAttr);
      newAttr = document.createAttribute("value");
      newAttr.nodeValue = toSel.options[i].value;
      newNode.setAttributeNode(newAttr);
      // actually append virtual node to DOM tree
      toDataContainer.appendChild(newNode);
      }
    }
  // error message for missing selection
  function selectionError()
    {alert("Must select something!")}
  /* ]]> */
  </script>
  <table border="0" class="ordered-selection-field">
    <tr>
      <td>
        <select id="form-widgets-credentialsPlugins-from"
                name="form.widgets.credentialsPlugins.from"
                class="required list-field"
                multiple="multiple" size="5">
        </select>
      </td>
      <td>
        <button onclick="javascript:from2to('form-widgets-credentialsPlugins')"
                name="from2toButton" type="button" value="→">&rarr;</button>
        <br />
        <button onclick="javascript:to2from('form-widgets-credentialsPlugins')"
                name="to2fromButton" type="button" value="←">&larr;</button>
      </td>
      <td>
        <select id="form-widgets-credentialsPlugins-to"
                name="form.widgets.credentialsPlugins.to"
                class="required list-field"
                multiple="multiple" size="5">
        </select>
        <input name="form.widgets.credentialsPlugins-empty-marker"
               type="hidden" />
        <span id="form-widgets-credentialsPlugins-toDataContainer">
          <script type="text/javascript">
            copyDataForSubmit('form-widgets-credentialsPlugins');</script>
        </span>
      </td>
      <td>
        <button onclick="javascript:moveUp('form-widgets-credentialsPlugins')"
                name="upButton" type="button" value="↑">&uarr;</button>
        <br />
        <button onclick="javascript:moveDown('form-widgets-credentialsPlugins')"
                name="downButton" type="button" value="↓">&darr;</button>
      </td>
    </tr>
  </table>
  </div>
            </div>
            <div id="form-widgets-authenticatorPlugins-row"
                 class="row">
                <div class="label">
                  <label for="form-widgets-authenticatorPlugins">
                    <span>Authenticator Plugins</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
  <script type="text/javascript">
  /*  <![CDATA[ */
  function moveItems(from, to)
    {
    // shortcuts for selection fields
    var src = document.getElementById(from);
    var tgt = document.getElementById(to);
    if (src.selectedIndex == -1) selectionError();
    else
      {
      // iterate over all selected items
      // --> attribute "selectedIndex" doesn't support multiple selection.
      // Anyway, it works here, as a moved item isn't selected anymore,
      // thus "selectedIndex" indicating the "next" selected item :)
      while (src.selectedIndex > -1)
        if (src.options[src.selectedIndex].selected)
          {
          // create a new virtal object with values of item to copy
          temp = new Option(src.options[src.selectedIndex].text,
                        src.options[src.selectedIndex].value);
          // append virtual object to targe
          tgt.options[tgt.length] = temp;
          // want to select newly created item
          temp.selected = true;
          // delete moved item in source
          src.options[src.selectedIndex] = null;
        }
      }
    }
  // move item from "from" selection to "to" selection
  function from2to(name)
    {
    moveItems(name+"-from", name+"-to");
    copyDataForSubmit(name);
    }
  // move item from "to" selection back to "from" selection
  function to2from(name)
    {
    moveItems(name+"-to", name+"-from");
    copyDataForSubmit(name);
    }
  function swapFields(a, b)
    {
    // swap text
    var temp = a.text;
    a.text = b.text;
    b.text = temp;
    // swap value
    temp = a.value;
    a.value = b.value;
    b.value = temp;
    // swap selection
    temp = a.selected;
    a.selected = b.selected;
    b.selected = temp;
    }
  // move selected item in "to" selection one up
  function moveUp(name)
    {
    // shortcuts for selection field
    var toSel = document.getElementById(name+"-to");
    if (toSel.selectedIndex == -1)
        selectionError();
    else if (toSel.options[0].selected)
        alert("Cannot move further up!");
    else for (var i = 0; i < toSel.length; i++)
      if (toSel.options[i].selected)
        {
        swapFields(toSel.options[i-1], toSel.options[i]);
        copyDataForSubmit(name);
        }
    }
  // move selected item in "to" selection one down
  function moveDown(name)
    {
      // shortcuts for selection field
      var toSel = document.getElementById(name+"-to");
      if (toSel.selectedIndex == -1) {
          selectionError();
      } else if (toSel.options[toSel.length-1].selected) {
          alert("Cannot move further down!");
      } else {
        for (var i = toSel.length-1; i >= 0; i--) {
          if (toSel.options[i].selected) {
            swapFields(toSel.options[i+1], toSel.options[i]);
          }
        }
        copyDataForSubmit(name);
      }
    }
  // copy each item of "toSel" into one hidden input field
  function copyDataForSubmit(name)
    {
    // shortcuts for selection field and hidden data field
    var toSel = document.getElementById(name+"-to");
    var toDataContainer = document.getElementById(name+"-toDataContainer");
    // delete all child nodes (--> complete content) of "toDataContainer" span
    while (toDataContainer.hasChildNodes())
        toDataContainer.removeChild(toDataContainer.firstChild);
    // create new hidden input fields - one for each selection item of
    // "to" selection
    for (var i = 0; i < toSel.options.length; i++)
      {
      // create virtual node with suitable attributes
      var newNode = document.createElement("input");
      var newAttr = document.createAttribute("name");
      newAttr.nodeValue = name.replace(/-/g, '.')+':list';
      newNode.setAttributeNode(newAttr);
      newAttr = document.createAttribute("type");
      newAttr.nodeValue = "hidden";
      newNode.setAttributeNode(newAttr);
      newAttr = document.createAttribute("value");
      newAttr.nodeValue = toSel.options[i].value;
      newNode.setAttributeNode(newAttr);
      // actually append virtual node to DOM tree
      toDataContainer.appendChild(newNode);
      }
    }
  // error message for missing selection
  function selectionError()
    {alert("Must select something!")}
  /* ]]> */
  </script>
  <table border="0" class="ordered-selection-field">
    <tr>
      <td>
        <select id="form-widgets-authenticatorPlugins-from"
                name="form.widgets.authenticatorPlugins.from"
                class="required list-field"
                multiple="multiple" size="5">
        </select>
      </td>
      <td>
        <button onclick="javascript:from2to('form-widgets-authenticatorPlugins')"
                name="from2toButton" type="button" value="→">&rarr;</button>
        <br />
        <button onclick="javascript:to2from('form-widgets-authenticatorPlugins')"
                name="to2fromButton" type="button" value="←">&larr;</button>
      </td>
      <td>
        <select id="form-widgets-authenticatorPlugins-to"
                name="form.widgets.authenticatorPlugins.to"
                class="required list-field"
                multiple="multiple" size="5">
        </select>
        <input name="form.widgets.authenticatorPlugins-empty-marker"
               type="hidden" />
        <span id="form-widgets-authenticatorPlugins-toDataContainer">
          <script type="text/javascript">
            copyDataForSubmit('form-widgets-authenticatorPlugins');</script>
        </span>
      </td>
      <td>
        <button onclick="javascript:moveUp('form-widgets-authenticatorPlugins')"
                name="upButton" type="button" value="↑">&uarr;</button>
        <br />
        <button onclick="javascript:moveDown('form-widgets-authenticatorPlugins')"
                name="downButton" type="button" value="↓">&darr;</button>
      </td>
    </tr>
  </table>
  </div>
            </div>
      </div>
    </div>
    <div>
      <div class="buttons">
  <input id="form-buttons-apply" name="form.buttons.apply"
         class="submit-widget button-field" value="Apply"
         type="submit" />
      </div>
    </div>
  </form>
  ...

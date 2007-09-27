======
README
======

The z3c.skin.ready2go package provides a skin including the layer called
IReady2GoBrowserLayer which is defined in z3c.layer.ready2go.

Note, this skin is only registered in the test layer. You can use this
skin as a base for your own custom skins or just use it as a sample for build
you own skins.

Open a browser and access our test skin called ``TestSkin``:

  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost/++skin++TestSkin')

Let's see how such a skin looks like:

  >>> print user.contents
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
        lang="en">
  <head>
  <title>Ready2go</title><meta http-equiv="cache-control" content="no-cache" />
  <meta http-equiv="pragma" content="no-cache" />
  <BLANKLINE>
  <BLANKLINE>
  <link rel="icon" type="image/png"
        href="http://localhost/++skin++TestSkin/@@/favicon.png" />
  </head>
  <body>
  <div id="layoutWrapper">
    <div id="layoutContainer">
      <div id="headerContainer">
        <div id="breadcrumbs" class="sortable">
  <BLANKLINE>
        </div>
        <div id="user">
          User: Manager
        </div>
        <img id="logo"
             src="http://localhost/++skin++TestSkin/@@/img/logo.gif"
             width="53" height="51" alt="logo" />
      </div>
      <div id="menuContainer">
  <ul>
    <li class="selected">
    <a href="http://localhost/++skin++TestSkin/index.html"><span>Home</span></a>
  </li>
  <BLANKLINE>
  </ul>
  <BLANKLINE>
  </div>
      <div id="naviContainer" class="sortable">
        Sidebar
  <BLANKLINE>
      </div>
      <div id="contentContainer">
        <div id="tabContainer"></div>
        <div id="content">
          <div>
    <br />
    <br />
    <h3>A system error occurred</h3>
    <br />
    <b>Please contact the administrator.</b>
    <a href="javascript:history.back(1);">
      Go back and try another URL.
    </a>
  </div>
  <BLANKLINE>
        </div>
      </div>
    </div>
  </div>
  </body>
  </html>
  <BLANKLINE>

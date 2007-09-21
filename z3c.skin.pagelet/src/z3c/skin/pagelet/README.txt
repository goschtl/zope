======
README
======

The z3c.skin.pagelet package provides a skin for the z3c.pagelet package.
Note, the pagelet skin is only registered in the test layer. You can use this
skin as a base for your own skins or just use it as a sample for the 
z3c.pagelet package.

Open a browser and access the ``Pagelet`` skin:

  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost/++skin++Pagelet')

Let's see how such a skin looks like:

  >>> print user.contents
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
        lang="en">
  <head>
  <base href="http://localhost/++skin++Pagelet/@@index.html" />
  <BLANKLINE>
  <meta http-equiv="cache-control" content="no-cache" />
  <meta http-equiv="pragma" content="no-cache" />
  <link type="text/css" rel="stylesheet"
        href="http://localhost/++skin++Pagelet/@@/pagelet.css"
        media="all" />
  <BLANKLINE>
  <script type="text/javascript">
          var contextURL='http://localhost/++skin++Pagelet/';</script>
  <BLANKLINE>
  <link rel="icon" type="image/png"
        href="http://localhost/++skin++Pagelet/@@/favicon.png" />
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
             src="http://localhost/++skin++Pagelet/@@/img/logo.gif"
             width="53" height="51" alt="logo" />
      </div>
      <div id="menuContainer"></div>
      <div id="naviContainer" class="sortable">
  <BLANKLINE>
      </div>
      <div id="contentContainer">
        <div id="tabContainer"></div>
        <div id="content">
          <div>This is the default index view</div>
  <BLANKLINE>
        </div>
      </div>
    </div>
  </div>
  </body>
  </html>
  <BLANKLINE>

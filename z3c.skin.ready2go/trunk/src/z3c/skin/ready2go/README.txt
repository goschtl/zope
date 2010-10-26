======
README
======

The z3c.skin.ready2go package provides a skin based on the called
IReady2GoBrowserLayer which is defined in z3c.layer.ready2go.

Note, this skin is only registered in the test layer. You can use this
skin as a base for your own custom skins or just use it as a sample for build
you own skins.

Open a browser and access our test skin called ``Ready2Go``:

  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost/++skin++Ready2Go')

Let's see how such a skin looks like:

  >>> print user.contents
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
        lang="en">
  <head>
  <base href="http://localhost/++skin++Ready2Go/@@index.html" />
  <BLANKLINE>
  <title>Ready2go</title><meta http-equiv="cache-control" content="no-cache" />
  <meta http-equiv="pragma" content="no-cache" />
  <script type="text/javascript">
    var contexturl = 'http://localhost/++skin++Ready2Go';
    var viewurl = 'http://localhost/++skin++Ready2Go/@@index.html';</script>
  <script type="text/javascript"
          src="http://localhost/++skin++Ready2Go/@@/ready2go.js"></script>
  <BLANKLINE>
  <link type="text/css" rel="stylesheet"
        href="http://localhost/++skin++Ready2Go/@@/ready2go.css"
        media="all" />
  <BLANKLINE>
  <link rel="icon" type="image/png"
        href="http://localhost/++skin++Ready2Go/@@/favicon.png" />
  </head>
  <body>
  <div id="layoutWrapper">
    <div id="layoutContainer">
      <div id="headerContainer">
        <div id="breadcrumbs" class="sortable">
  <BLANKLINE>
        </div>
        <div id="user">
          <span>User:</span>
          <span>Fallback unauthenticated principal</span>
          &nbsp;&nbsp;
          <a href="http://localhost/++skin++Ready2Go/logout.html"
             style="font-size: 100%">[Logout]</a>
        </div>
        <img id="logo"
             src="http://localhost/++skin++Ready2Go/@@/img/logo.gif"
             width="53" height="51" alt="logo" />
      </div>
      <div id="menuContainer">
  <BLANKLINE>
        <div id="addingMenuContainer">
          <ul id="addingMenu" class="addingMenu">
            <li class="menuSeparatorLeft">
              <a href="#">Adding</a>
  <BLANKLINE>
            </li>
          </ul>
        </div>
      </div>
      <div id="naviContainer">
  <BLANKLINE>
      </div>
      <div id="contentContainer">
        <div id="contextMenuContainer">
  <BLANKLINE>
          <div id="contextMenuContainerBottom">
            &nbsp;
          </div>
        </div>
        <div id="content">
          test page
  <BLANKLINE>
        </div>
      </div>
    </div>
  </div>
  </body>
  </html>
  <BLANKLINE>

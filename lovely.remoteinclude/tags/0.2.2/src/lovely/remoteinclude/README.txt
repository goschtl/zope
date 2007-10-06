=========================
Remote Includes Renderers
=========================

This package allows to render include views of viewlets and views
which implement the IContentProvider interface. This is done by
a subscriber on BeforeUpdateEvent.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

If we include it in a pagetemplate, includes are rendered.

  >>> browser.open('http://localhost/@@test.html')
  >>> print browser.contents
  <html>
  <body>
  <div>
  This is the real content of inc1
  </div>
  <BLANKLINE>
  <!--# include virtual="/inc2.html" -->
  <!--# include virtual="/inc3.html" -->
  </body>
  </html>

But not if accessed directly, the real content is rendered.

  >>> browser.open('http://localhost/@@inc2.html')
  >>> browser.contents
  '<div>\n  This is the real content of inc2\n</div>\n'

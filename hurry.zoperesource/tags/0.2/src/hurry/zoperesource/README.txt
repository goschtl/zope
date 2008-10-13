Zope integration for hurry.resource
***********************************

This package provides Zope integration for hurry.resource. This means
three taking care of three things:

* maintain the needed resources throughout the request/response cycle.

* know how to make a URL to a resource.

* make so that resource references are automatically inserted in the
  HTML header.

This library fulfills these conditions for a Zope 3/Grok setup.

We'll run through a few tests to demonstrate it. Note that the real
code being tested is not in this document itself, but in the views described
in ``ftesting.zcml``.

We need to be in a request to make this work, so let's up a request to
a page we have set up in ``ftesting.zcml`` that should cause the
inclusion of a single resource in its header::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open('http://localhost/hurry.zoperesource.test_single')
  >>> print browser.contents 
  <html>
  <head>
      <script type="text/javascript" src="http://localhost/@@/foo/a.js"></script>
  <BLANKLINE>
  </head>
  <body>
  <p>the widget HTML itself</p>
  </body>
  </html>

If a resource happens to need another resource, this resource is also
automatically included::

  >>> browser.open('http://localhost/hurry.zoperesource.test_multiple')
  >>> print browser.contents 
  <html>
  <head>
      <script type="text/javascript" src="http://localhost/@@/foo/a.js"></script>
    <script type="text/javascript" src="http://localhost/@@/foo/b.js"></script>
  <BLANKLINE>
  </head>
  <body>
  <p>the widget HTML itself</p>
  </body>
  </html>

Let's force all javascript resources to be forced to be included at
the bottom now, just before the ``</body>`` tag::

  >>> browser.open('http://localhost/hurry.zoperesource.test_bottom')
  >>> print browser.contents 
  <html>
  <head>
  </head>
  <body>
  <p>the widget HTML itself</p>
  <script type="text/javascript" src="http://localhost/@@/foo/a.js"></script>
  <script type="text/javascript" src="http://localhost/@@/foo/b.js"></script></body>
  </html>

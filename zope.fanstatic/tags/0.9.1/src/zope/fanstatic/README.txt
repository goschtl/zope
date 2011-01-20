Zope integration for fanstatic
******************************

This package provides Zope integration for fanstatic. This means it's
taking care of three things:

* provide access to the needed resources throughout the request/response cycle.

* provide the base URL for the resources to be rendered.

* clear the needed resources when an exception view is rendered.

This library fulfills these conditions for a Zope Toolkit/Grok setup.

We'll run through a few tests to demonstrate it. Note that the real
code being tested is not in this document itself, but in the views
described in ``ftesting.zcml``.

We need to be in a request to make this work, so let's up a request to
a page we have set up in ``ftesting.zcml`` that should cause the
inclusion of a single resource in its header::

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/zope.fanstatic.test_single')
  >>> print browser.contents
  <html>
  <head>
  <script type="text/javascript" src="http://localhost/fanstatic/foo/a.js"></script>
  <BLANKLINE>
  </head>
  <body>
  <p>the widget HTML itself</p>
  </body>
  </html>

If a resource happens to need another resource, this resource is also
automatically included::

  >>> browser.open('http://localhost/zope.fanstatic.test_multiple')
  >>> print browser.contents
  <html>
  <head>
    <script type="text/javascript" src="http://localhost/fanstatic/foo/a.js"></script>
    <script type="text/javascript" src="http://localhost/fanstatic/foo/b.js"></script>
  <BLANKLINE>
  </head>
  <body>
  <p>the widget HTML itself</p>
  </body>
  </html>

Let's force all javascript resources to be forced to be included at
the bottom now, just before the ``</body>`` tag::

  >>> browser.open('http://localhost/zope.fanstatic.test_bottom')
  >>> print browser.contents
  <html>
  <head>
  </head>
  <body>
  <p>the widget HTML itself</p>
  <script type="text/javascript" src="http://localhost/fanstatic/foo/a.js"></script>
  <script type="text/javascript" src="http://localhost/fanstatic/foo/b.js"></script></body>
  </html>

In-template resources
---------------------

zope.fanstatic provides support for rendering resource publisher
aware URLs to in-template resources::

  >>> browser.open('http://localhost/zope.fanstatic.test_inline_resource')
  >>> print browser.contents
  <html>
  <head>
  </head>
  <body>
    <img src="http://localhost/fanstatic/foo/evencaveman.jpg" />
    <img src="http://localhost/fanstatic/foo/sub/evencaveman.jpg" />
  </body>
  </html>

Exception views
---------------

When an exception occurs in the rendering of a view, we don't want to have any
needed resources intended for a view being also injected in the error view.
The needed resources are cleared and if the exception view chooses to do so,
it can need resources itself.

  >>> browser.raiseHttpErrors = False
  >>> browser.open('http://localhost/zope.fanstatic.test_error')
  >>> import fanstatic
  >>> fanstatic.get_needed().has_resources()
  False

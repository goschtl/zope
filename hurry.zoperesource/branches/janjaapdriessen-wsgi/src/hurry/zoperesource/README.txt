Zope integration for hurry.resource
***********************************

This package provides Zope integration for hurry.resource. This means
it's taking care of two things:

* provide access to the needed resources in the WSGI environment
  throughout the request/response cycle.

* provide the base URL for the resources to be rendered.

This library fulfills these conditions for a Zope Toolkit/Grok setup.

We'll run through a few tests to demonstrate it. Note that the real
code being tested is not in this document itself, but in the views
described in ``ftesting.zcml``.

We need to be in a request to make this work, so let's up a request to
a page we have set up in ``ftesting.zcml`` that should cause the
inclusion of a single resource in its header::

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open('http://localhost/hurry.zoperesource.test_single')
  >>> print browser.contents
  <html>
  <head>
  <script type="text/javascript" src="http://localhost/fanstatic/:hash:.../foo/a.js"></script>
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
    <script type="text/javascript" src="http://localhost/fanstatic/:hash:.../foo/a.js"></script>
    <script type="text/javascript" src="http://localhost/fanstatic/:hash:.../foo/b.js"></script>
  <BLANKLINE>
  </head>
  <body>
  <p>the widget HTML itself</p>
  </body>
  </html>

Let's force all javascript resources to be forced to be included at
the bottom now, just before the ``</body>`` tag::

  >>> import hurry.resource
  >>> browser.open('http://localhost/hurry.zoperesource.test_bottom')
  >>> print browser.contents
  <html>
  <head>
  </head>
  <body>
  <p>the widget HTML itself</p>
  <script type="text/javascript" src="http://localhost/fanstatic/:hash:.../foo/a.js"></script>
  <script type="text/javascript" src="http://localhost/fanstatic/:hash:.../foo/b.js"></script></body>
  </html>

In-template resources
---------------------

Hurry.zoperesource provides support for rendering resource publisher
aware URLs to in-template resources::

  >>> browser.open('http://localhost/hurry.zoperesource.test_inline_resource')
  >>> print browser.contents
  <html>
  <head>
  </head>
  <body>
    <img src="http://localhost/fanstatic/:hash:.../foo/evencaveman.jpg" />
    <img src="http://localhost/fanstatic/:hash:.../foo/sub/evencaveman.jpg" />
  </body>
  </html>



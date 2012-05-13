grokcore.resource
=================

`grokcore.resource` can be used to integrate fanstatic_ resources into Grok
applications. When not using grokcore.resource, fanstatic resources are
typically `needed` in the `update` method of a view or view component.

grokcore.resource moves the definition of what resources come with a view
to the configuration layer. Using the `grokcore.resource.resources` directive,
one or more resources can be associated to a view or view component as such::

  from mypackage.resource import a, b

  class DocTest(grok.View):
      grokcore.resource.resources(a, b)

When rendering this view, the resources a and b will be automatically
registered with fanstatic; fanstatic takes care of rendering the resource URLs
into the result html::

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser('http://localhost/doctest')
  >>> print browser.contents
  <html>
  <head>
    <link rel="stylesheet" type="text/css"
          href="http://localhost/fanstatic/grokcore.resource.tests/a.css" />
    <link rel="stylesheet" type="text/css"
          href="http://localhost/fanstatic/grokcore.resource.tests/b.css" />
  </head>
  <body>
  </body>
  </html>

Supported view components
-------------------------

The grok.View, grok.Layout, grok.Viewlet and grok.ContentProvider components
are supported by grokcore.resource.

.. _fanstatic: http://www.fanstatic.org/

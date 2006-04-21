zope.browserzcml2
=================

This package provides a few ZCML directives to register a browser
pages in a much less magical way.  The rationale behind this is that
pages implemented in Python should themselves be fully operational, in
other words, publishable as registered adapters.  These directives are
all part of the ``http://namespaces.zope.org/browser2`` namespace.

In the following we will discuss three major use cases involving
browser pages for which this package provides three ZCML directives:

  * ``browser2:page``

  * ``browser2:pageTemplate``

  * ``browser2:pagesFromClass``


Pages
-----

A browser page is nothing but a (browser) view that is *publishable*.
Publishable means that it is basically the last piece in the traversal
chain and the object that is responsible for the request.  It will be
published.  Hence, it has to be publishable.  Publishability is
determined by the ``IBrowerPublisher`` interface.  All pages should
provide it.

Simple page
~~~~~~~~~~~

Let's create a simple page.  For convenience, we can inherit from
``zope.formlib.Page`` which will give us ``IBrowserPublisher``
conformance:

  >>> import zope.formlib
  >>> class MacGyverPage(zope.formlib.Page):
  ...     def __call__(self):
  ...         return u"I've got a Swiss Army knife"

Now we register the page.  This works almost like registering an
adapter:

  >>> run_config("""
  ... <browser2:page
  ...     for="*"
  ...     name="simplepage.html"
  ...     factory="zope.browserzcml2.README.MacGyverPage"
  ...     permission="zope.Public"
  ...     />
  ... """)

Then we can look up the page as an adapter.  We'll use a test request
and a stub object.

  >>> import zope.component
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> page = zope.component.getMultiAdapter((object(), request),
  ...                                       name=u'simplepage.html')

We see that the adapter is an instance of our page class above and
that we get the expected result upon calling it.

  >>> page #doctest: +ELLIPSIS
  <zope.browserzcml2.README.MacGyverPage object at ...>
  >>> page()
  u"I've got a Swiss Army knife"

Other factories
~~~~~~~~~~~~~~~

Note that we require the page factory to implement
``IBrowserPublisher``.  Something else won't work, e.g.:

  >>> from zope.app.publisher.browser import BrowserView
  >>> class MacGyverView(BrowserView):
  ...     def __call__(self):
  ...         return u"I drive a Jeep"

  >>> run_config("""
  ... <browser2:page
  ...     for="*"
  ...     name="justaview.html"
  ...     factory="zope.browserzcml2.README.MacGyverView"
  ...     permission="zope.Public"
  ...     />
  ... """) # doctest: +NORMALIZE_WHITESPACE
  Traceback (most recent call last):
    ...
  ZopeXMLConfigurationError: File "<string>", line 6.0-11.6
      ConfigurationError: The browser page factory needs to provide
      IBrowserPublisher. A convenient base class is zope.formlib.Page.

It is, however, absolutely possible that the supplied factory isn't in
fact a class.  As long as it implements ``IBrowserPublisher``, it's
ok:

  >>> import zope.interface
  >>> from zope.publisher.interfaces.browser import IBrowserPublisher
  >>> @zope.interface.implementer(IBrowserPublisher)
  ... def makeAMacGyverPage(context, request):
  ...     return MacGyverPage(context, request)

  >>> run_config("""
  ... <browser2:page
  ...     for="*"
  ...     name="functionfactory.html"
  ...     factory="zope.browserzcml2.README.makeAMacGyverPage"
  ...     permission="zope.Public"
  ...     />
  ... """)

  >>> page = zope.component.getMultiAdapter((object(), request),
  ...                                       name=u'functionfactory.html')
  >>> page #doctest: +ELLIPSIS
  <zope.browserzcml2.README.MacGyverPage object at ...>
  >>> page()
  u"I've got a Swiss Army knife"

Page with page template
~~~~~~~~~~~~~~~~~~~~~~~

Rendering HTML from Python is tedious.  We therefore often turn this
work over to Page Templates.  Referring to a Page Template in a page
is easy:

  >>> from zope.app.pagetemplate import ViewPageTemplateFile
  >>> class MacGyverTemplatePage(zope.formlib.Page):
  ...     __call__ = ViewPageTemplateFile('test.pt')

The rest works just like with a pure-Python browser page:

  >>> run_config("""
  ... <browser2:page
  ...     for="*"
  ...     name="templatepage.html"
  ...     factory="zope.browserzcml2.README.MacGyverTemplatePage"
  ...     permission="zope.Public"
  ...     />
  ... """)

  >>> page = zope.component.getMultiAdapter((object(), request),
  ...                                       name=u'templatepage.html')
  >>> page #doctest: +ELLIPSIS
  <zope.browserzcml2.README.MacGyverTemplatePage object at ...>
  >>> page()
  u"Hi, the name's MacGyver.\n"


Pages from Page Templates
-------------------------

We've just seen how to create pages that use Page Templates for
rendering.  If that's all a page does, we can use a shortcut provided
by the ``browser2:pageTemplate`` directive.  It works almost like the
``browser2:page`` directive, except that it takes a ``template``
parameter, not a ``factory`` parameter:

  >>> run_config("""
  ... <browser2:pageTemplate
  ...     for="*"
  ...     name="pagetemplate.html"
  ...     template="test.pt"
  ...     permission="zope.Public"
  ...     />
  ... """)

We can look up the page like the others before, except now it won't be
an instance of a class that we've implemented.  It'll be a dynamically
generated class.  Either way, we are still able to call it like any
other browser page:

  >>> page = zope.component.getMultiAdapter((object(), request),
  ...                                       name=u'pagetemplate.html')
  >>> page #doctest: +ELLIPSIS
  <zope.browserzcml2.zcml.TemplatePage object at ...>
  >>> page()
  u"Hi, the name's MacGyver.\n"


Pages from classes
------------------

XXX


Conflicts
---------

XXX

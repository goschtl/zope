.. _man-browser-page:

Browser Page
============

.. _man-browser-intro:

Introduction
------------

In the last chapter we have seen how to use resources HTML.  The resource
HTML will be only available on site-level with the ``@@`` prefix.  Where as
browser pages are accessed with a single ``@`` just before the page name.

Browser page (or more generically views) are representations for particular
objects/components.

If you have a template like this (``helloworld.pt``)::

  Hello, World !

To register a page with the above template for an ``IFolder`` interface::

  <browser:page
    name="helloworld.html"
    for="zope.site.interfaces.IFolder"
    template="helloworld.pt"
    permission="zope.Public"
    /> 

The ``browser:page`` directive is used to register browser pages.  The
`name` attribute specify the name of page which is used in the URL.  The
above page can be accessed from this URL:
http://localhost:8080/@helloworld.html

.. _man-browser-view:

View components
---------------

While templates display data view components are preparing data.  View
components convert data to output formats also prepare related data
(meta-data).  Then, create TAL-friendly object structures (dicts and lists).
View components know about: component for which the representation is
created (context) and request object holding all `output media` information
(request)


Implementation
~~~~~~~~~~~~~~

The organization of the browser code is really up to you and the above
examples are just the most basic rules of thumb.

Here is a simple view defined::

  from zope.formlib import form
  from zope.formlib import DisplayForm
  from zope.site.interfaces import IFolder

  class HelloWorld(DisplayForm):

      form_fields = form.Fields(IHelloWorld)

      def subFolderIds(self):
          for name, subobj in self.context.items():
              if IFolder.providedBy(subobj):
                  yield name 

Since methods and attributes of the view component are directly used by the
template, they should return simple iterable objects (e.g. lists, tuples,
generators) or mappings (e.g. dicts).

.. _man-browser-conclusion:

Conclusion
----------

This chapter introduced Browser pages.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the discussion
  thread.</a></noscript><a href="http://disqus.com" class="dsq-brlink">blog
  comments powered by <span class="logo-disqus">Disqus</span></a>

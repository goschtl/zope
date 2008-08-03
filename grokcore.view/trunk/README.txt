THis package provides support for writing browser pages for Zope
and registering them directly in Python (without ZCML).

.. contents::

Setting up ``grokcore.view``
============================

This package is essentially set up like the `grokcore.component`_
package, please refer to its documentation for details.  The
additional ZCML line you will need is::

  <include package="grokcore.view" file="meta.zcml" />
  <include package="grokcore.view" />

Put the first line somewhere near the top of your root ZCML file (but
below the line where you include ``grokcore.component``'s
configuration) and the second line somewhere next to your other
dependency includes.


Examples
========

Browser page
------------

A browser page is implemented by subclassing the
``grokcore.view.View`` baseclass.  At a minimum, a browser page must
have

1. either an associated template or a ``render()`` method

2. a context that it's registered for as a view

3. a name (which is, if not specified explicitly, the class's name in
   lower case characters).

For example, the following class defines a view that's registered for
all objects and simply prints "Hello World!"::

  import grokcore.view
  import zope.interface

  class Hello(grokcore.view.View):
      grokcore.view.context(zope.interface.Interface)

      def render(self):
          self.response.setHeader("Content-Type", "text/plain")
          return "Hello World!"

Here we've made use of the implicit name feature.  This class will be
available as the ``hello`` view for all objects.  So for instance,
you'll be able to invoke it with URLs like::

  http://localhost/some/obj/hello

We could also have spelled this out explicitly::

  class Hello(grokcore.view.View):
      grokcore.view.context(zope.interface.Interface)
      grokcore.view.name('hello')

      ...

Of course, more than often a view should render HTML which you would
construct using some sort of templating engine.  ``grokcore.view``
comes with built-in support for Zope's PageTemplate engine.  By
convention, PageTemplate templates end with the ``.pt`` extension.

So let our ``Hello`` view render HTML instead of plain text, we remove
the ``render()`` method from the class and instead we create a
template, e.g. like so::

  <html>
  <body>
    <p>Hello <span tal:replace="request/principal/title" />!</p>
  </body>
  </html>

This will greet a logged in user with his or her actual name.

To associate the template with the view, we have to put it in a
certain place.  Let's say the ``Hello`` view class from above was in
an ``app.py`` module.  Then we create an ``app_templates`` directory
next to it and place the template file in there (the name of this
directory can be customized with the ``templatedir`` directive, see
below).  The file name can be anything as long as the extension is
``.pt``.  However, we can again make use of a convention here.  If we
name the template like the class (except in lower case characters),
then the template and the class are associated automatically.  If not,
we would have to use the ``template`` directive on the view class to
spell out the name of the template file explicitly.

To cut a long story short, if we named it ``app_templates/hello.pt``,
it would be found automatically.

Layers and skins
----------------

To define a browser layer, simply extend the ``IBrowserRequest``
interface::

  class IGreenLayer(grokcore.view.IBrowserRequest):
      pass

If you then wanted to define a skin, simply inherit from all the layer
interfaces that should be in the skin and use the ``skin()`` directive
to give the layer a name::

  class IGreenSkin(IGreenLayer, grokcore.view.IDefaultBrowserLayer):
      grokcore.view.skin('Green')


API overview
============

Base classes
------------

``View``
    Base class for browser pages.  Use the ``context`` directive to
    specify the view's context.  Use the ``name`` directive to set the
    view's name; if not used, the view's name will be the class's name
    in lower case characters.  You may also use the ``template``
    directive to specify the name of the template file that should be
    associated with the view as well as the ``layer`` directive to
    specify which layer it should be on if not the default layer.

Directives
----------

``templatedir(dirname)``
     Module-level directive that tells the template machinery which
     directory to look in for templates that should associated with
     views in a particular module.  If not used, it defaults to
     ``<module_name>_templates``.

``template(filename_wo_ext)``
    Class-level directive that specifies the name a template file
    that's associated with a view class, *without* the file extension.
    If not used, it defaults to the class's name in lower case
    characters.

``layer(layer_interface)``
    Class-level directive that defines which layer the view is
    registered on.  If not used, it defaults to the
    ``IDefaultBrowserLayer``.

``skin(skin_name)``
    Directive used on a layer interface to register it as skin using a
    human-readable name (``skin_name``).

Other
-----

``url(request, obj, name=None, data=None)``
    Generate the URL to an object, with an optional view name
    attached.  The ``data`` argument can be a dictionary whose
    contents is converted into the a query string that's appended to
    the URL.

``PageTemplate(template_code)``
    Create an inline PageTemplate object.

``PageTemplateFile(filename)``
    Create a PageTemplate object from a file.

``IBrowserRequest``
    Browser request interface from ``zope.publisher``.

``IDefaultBrowserLayer``
    Default layer for browser components from ``zope.publisher``.


In addition, the ``grokcore.security`` package exposes the
`grokcore.component`_ and `grokcore.security`_ APIs.

.. _grokcore.component: http://pypi.python.org/pypi/grokcore.component
.. _grokcore.security: http://pypi.python.org/pypi/grokcore.security
.. _grokcore.view: http://pypi.python.org/pypi/grokcore.view

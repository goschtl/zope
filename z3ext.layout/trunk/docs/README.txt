Browser layout and page system
==============================

The ``z3ext.layout`` package implements a flexible way to create browser pages
with higly customizable layouts and dipsplay logic.

This package registers browser pages as (context, request) adapters, so they
are simple views in a zope world. But the pages created by this package are very
smart. The main feature is extremely powerful content/layout separation mechanism,
including support for multiple layouts for different types of content, views and
skins, nested layouts, pluggable templates etc.

In the following chapters, we well use two main terms:

* pagelet - the "content" part of a browser page.
* layout - the layout in which pagelet is rendered.


Basic usage
-----------

This chapter will show you how to create a page from template, class or both,
and how to define a layout for them.

Note, that we will use ZCML directives in the "z3ext" namespace, to make them
available, you need to define that namespace pointing to "http://namespaces.zope.org/z3ext"
in your ``configure.zcml`` file. Example::

  <configure
      xmlns="http://namespaces.zope.org/zope"
      xmlns:z3ext="http://namespaces.zope.org/z3ext"
      >

    ... some directives in the "z3ext" namespace"

  </configure>


Creating pages
~~~~~~~~~~~~~~

As said above, the page consist of the "pagelet" and "layout", in this chapter
we will talk about creating pagelets. To create a pagelet, we use the
``z3ext:pagelet`` ZCML directive. 


Providing only a template
+++++++++++++++++++++++++

One of the simplest cases is when you want to create a templated page for a
content type, let's show how it's done::

  <z3ext:pagelet
    for=".interfaces.IContent"
    name="index.html"
    template="content.pt"
    />

In the example above, we created a pagelet named "index.html" for objects
providing "IContent" interface using template in the "content.pt" file. Note,
that did not specify access permission for this pagelet, that means that this
pagelet is public, so it will be accessible without restrictions.

When accessed, this pagelet will be rendered using default unnamed layout, or
if layout can not be found, it will be rendered without any layout. We'll
talk about layouts a bit later.

The template variables available in pagelet's templates are the same as with
standard zope view templates (using ``ViewPageTemplateFile`` class from the
``zope.app.pagetemplate`` package):

* ``context`` - the context object
* ``request`` - the request object
* ``view`` - the view object that uses this template
* ``template`` - the template object (for accessing macros for example)
* ``nothing`` - the None object


Providing a template and a class
++++++++++++++++++++++++++++++++

If you want to provide some logic in the pagelet, such as getting needed values
or processing some request arguments, you can provide a mix-in class. z3ext
pagelet system uses the update/render pattern, so pagelet classes have the
"update" method that performs required actions, and the "render" method that
does the rendering of pagelet.

The default "render" method does rendering of the pagelet's template and the
default "update" method does nothing. So, if we want to use a template, but
include some logic before template is rendered, we need to provide own "update"
method.

Let's create a "smart" helloworld-type pagelet class::

  class GreeterPage(object):
  
      def update(self):
          self.who = self.request.get('who', 'World')

As you can see, it sets the "who" attribute to itself, getting the data from
the request. From a template, it can be accessed via "view" variable::

  <p>
    Hello, <span tal:replace="view/who" />!
  </p>

Finally, register the pagelet with ZCML directive, passing the mix-in class
as the "class" argument::

  <z3ext:pagelet
    for="*"
    name="hello.html"
    template="hello.pt"
    class=".GreeterPage"
    />

Note that in the example above we used asterisk ("*" sign) in "for" argument,
that means that the pagelet is registered for any type of object.

Providing only a class
++++++++++++++++++++++

There is two cases when you want to only provide a class and don't provide any
template for a pagelet:

1. You want to implement custom rendering.
2. You want template to be provided separately, in other place or be dependent
   on a browser skin/layer.

z3ext pagelets support both.

In a first case, you need to provide a class with custom "render" method that
should return a string ready to include in a layout.

Let's give an example of such class::

  class CustomRender(object):
  
      def render(self):
          return u'<p>Hello world!</p>'

This class doesn't need any templates, as it renders the ready-to-use HTML
content. It can be registered without specifying the "template" argument::

  <z3ext:pagelet
    for="*"
    name="hello2.html"
    class=".CustomRenderPage"
    />


In a second case, when you want to provide template separately, you shouldn't
override the "default" render behaviour and shouldn't provide a template when
registering a pagelet.

Let's use for example a "smart" greeter view class we used above::

  class GreeterPage(object):
  
      def update(self):
          self.who = self.request.get('who', 'World')

But now, we'll register it without providing a template::

  <z3ext:pagelet
    for="*"
    name="hello3.html"
    class=".GreeterPage"
    />

What the default "render" implementation will do is try to search an unnamed
pagelet for this pagelet and current request object.

So, to register a template for the pagelet above, we need to register a
templated pagelet passing this pagelet in the "for" argument, without specifying
a name::

  <z3ext:pagelet
    for=".GreeterPage"
    template="hello.pt"
    />

As you may notice, this trick gives even more control of rendering, because you
can provide custom logic for that "template pagelet", giving another class via
"class" argument. This can be extremely useful when you want to provide additional
logic when rendering third-party pagelets in your skins.


Creating layouts
~~~~~~~~~~~~~~~~

This chapter describes the layouts mechanism and ways of defining layouts.

In the previous chapter we described how to create differently rendered pagelets.
But all pagelets, when accessed from a browser are renderd into some layout.

Every web site nowadays has common look and feel thru all its pages, so it makes
sense to define layout separately. Moreover, in complex web applications, some
parts has different "sub-layout" inside one common layout. This is greatly
supported by the ``z3ext.layout`` package.

Basics
++++++

So, to define a layout, we use the another ZCML directive, named ``z3ext:layout``.
By default, pagelets use unnamed layout, registered either for a pagelet, or
content object, or both.

What layout does is rendering a pagelet framed in some layout elements, so let's
create such template. The pagelet is available as "view" variable in the template,
so it can call its "render" method::

  <html>
   <head>
    <title>Example layout</head>
   </head>
   <body tal:content="structure view/render">
    Here comes the content...
   </body>
  </html> 

Now let's register this template as a layout for our ``GreeterPage`` pagelet,
that we created in previous chapter::

  <z3ext:layout
    view=".GreeterPage"
    template="layout.pt"
    />

If we want to provide another layout for the same pagelet, but for different
content type, we can register it specifying the "for" argument::

  <z3ext:layout
    for=".interfaces.ISomeContentMarker"
    view=".GreeterPage"
    template="layout2.pt"
    />

So, everything besides objects providing ``ISomeContentMarker`` will use
"layout.pt" template and ``ISomeContentMarker`` objects will use "layout2.pt"
template for the ``GreeterPage`` pagelet.


Nested layouts
++++++++++++++

Very often we need to use several layouts for different pages that still have
some common parent layout. Here nested named layouts come to help.

In the previous section, we registered basic HTML structure as a layout for
our pagelet. But let's imagine, that that basic HTML structure is required
for all pages in our web portal, but one of pagelets, the ``GreeterPage`` needs
additional layout needed for its presentation. To implement that, first, let's
register our basic HTML structure as a layouts named "portal"::

  <z3ext:layout
    for="*"
    name="portal"
    template="layout.pt"
    />

That means exactly that for any object there's a layout named "portal" that uses
the "layout.pt" template.

Now, let's create a "sub-layout" template for our greeter page::

  <div class="greeter" tal:content="structure view/render">
    here comes content
  </div>

We register it for our ``GreeterPage`` just like we we did it first time,
excepting that we specify additional argument - "layout" that is a name
to a parent layout::

  <z3ext:layout
    view=".GreeterPage"
    template="greeter_layout.pt"
    layout="portal"
    />

So, now our greeter page will be rendered somewhat like this::

  <html>
   <head>
    <title>Example layout</head>
   </head>
   <body>
    <div class="greeter">
     <p>
      Hello, World!
     </p>
    </div>
   </body>
  </html> 

The original pagelet template is rendered in its sub-layout which is rendered
in its parent layout. The depth of nesting is not restricted, so you can create
sub-sub-layouts and so on.

.. note::

  The ``z3ext.layout`` package has some default layout configuration defined in
  its "configure.zcml" file. This configuration is used by the z3ext default
  browser UI.

  First, it defines a default unnamed layout with a template containing a
  "div" element that wraps the content of a pagelet.
  
  Second, that unnamed layout has a parent layout named "viewspace" that also
  adds its own wrapper HTML elements.
  
  Third, the "viewspace" layout has another parent layout named "workspace",
  that, again adds more wrapper HTML elements.
  
  And finally, the "workspace" has the "portal" layout as its parent that
  wraps the content with some HTML elements and renders status messages above.
  
  The "portal" layout uses the zope3 "standard_macros" concept to render itself,
  so it will work with skins like "Rotterdam" or "Boston" from zope3. But if
  you are not planning to integrate z3ext pagelets with those skins, you can
  simply override the "portal" layout for your skin.
  
  The power in this is that you can override layout at any level for any pagelet
  or content object, adding your own page elements or changing existing ones.


Layout template variables
+++++++++++++++++++++++++

In addition to standard view template variables (context, request, view,
template, nothing), layout templates has additional variables:

* ``layout`` - the layout object which is similar to "view objects", but used for
  layouts. The custom view objects are described in the "Advanced usage" part
  of this document.

* ``mainview`` - the original pagelet that is requested the layout. In case of
  nested layouts, the "view" variable points to a sub-layout, so if you want to
  access the real pagelet, use this variable.

* ``maincontext`` - ???

* ``layoutcontext`` - ???

Advanced usage
--------------

TODO:

* describe location-aware layout querying
* describe "pagelet" publisher and tal expression
* full description of ZCML directives: pagelet, layout, pageletType
* additional/custom layout logic (specifying mixin class for layouts).

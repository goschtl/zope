hurry.resource
==============

Introduction
------------

Resources are files that are used as resources in the display of a web
page, such as CSS files, Javascript files and images. Resources
packaged together in a directory to be published as such are called a
resource *library*.

When a resource is included in the ``head`` section of a HTML page, we
call this a resource *inclusion*. An inclusion is of a particular
resource in a particular library. There are two forms of this kind of
inclusion in HTML: javascript is included using the ``script`` tag,
and CSS (and KSS) are included using a ``link`` tag.

Inclusions may depend on other inclusions. A javascript resource may
for instance be built on top of another javascript resource. This
means both of them should be loaded when the page display, the
dependency before the resource that depends on it.

Page components may actually require a certain inclusion in order to
be functional. A widget may for instance expect a particular
Javascript library to loaded. We call this an *inclusion requirement* of
the component.

``hurry.resource`` provides a simple API to specify resource
libraries, inclusion and inclusion requirements.

A resource library
------------------

We define a library ``foo``::

  >>> from hurry.resource import Library
  >>> foo = Library('foo')

Inclusion
---------

We now create an inclusion of a particular resource in a library. This
inclusion needs ``a.js`` from ``library`` and ``b.js`` as well::

  >>> from hurry.resource import ResourceInclusion
  >>> x1 = ResourceInclusion(foo, 'a.js')
  >>> x2 = ResourceInclusion(foo, 'b.css')

Let's now make an inclusion ``y1`` that depends on ``x1`` and ``x2``::

  >>> y1 = ResourceInclusion(foo, 'c.js', depends=[x1, x2])

Inclusion requirements
----------------------

When rendering a web page we want to require the inclusion of a
resource anywhere within the request handling process. We might for
instance have a widget that takes care of rendering its own HTML but
also needs a resource to be included in the page header.

We have a special object that represents the needed inclusions during
a certain request cycle::

  >>> from hurry.resource import NeededInclusions
  >>> needed = NeededInclusions()

We state that a resource is needed by calling the ``needed`` method on
this object::

  >>> needed.need(y1)

Let's now see what resources are needed by this inclusion::

  >>> needed.inclusions()
  [<ResourceInclusion 'b.css' in library 'foo'>, 
   <ResourceInclusion 'a.js' in library 'foo'>, 
   <ResourceInclusion 'c.js' in library 'foo'>]

As you can see, ``css`` resources are sorted before ``js`` resources.

A convenience spelling
----------------------

When specifying that we want a resource inclusion to be rendered, we
now need access to the current ``NeededInclusions`` object and the
resource inclusion itself.

Let's introduce a more convenient spelling of needs now::

  y1.need()

We can require a resource without reference to the needed inclusions
object directly as there is typically only a single set of needed
inclusions that is generated during the rendering of a page.  

So let's try out this spelling to see it fail::

  >>> y1.need()
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.resource.interfaces.ICurrentNeededInclusions>, '')

We get an error because we haven't configured the framework yet. The
system says it cannot find the utility component
``ICurrentNeededInclusions``. This is the utility we need to define
and register so we can tell the system how to obtain the current
``NeededInclusions`` object. Our task is therefore to provide a
``ICurrentNeededInclusions`` utility that can give us the current
needed inclusions object.

This needed inclusions should be maintained on an object that is going
to be present throughout the request/response cycle that generates the
web page that has the inclusions on them. The most obvious place where
we can maintain the needed inclusions is the request object
itself. Let's introduce such a simple request object (your mileage may
vary in your own web framework)::

  >>> class Request(object):
  ...    def __init__(self):
  ...        self.needed = NeededInclusions()

We now make a request, imitating what happens during a typical
request/response cycle in a web framework::

  >>> request = Request()

We should define a ``ICurrentNeededInclusion`` utility that knows how
to get the current needed inclusions from that request::

  >>> def currentNeededInclusions():
  ...    return request.needed

  >>> c = currentNeededInclusions

We need to register the utility to complete plugging into the
``INeededInclusions`` pluggability point of the ``hurry.resource``
framework::

  >>> from zope import component
  >>> from hurry.resource.interfaces import ICurrentNeededInclusions
  >>> component.provideUtility(currentNeededInclusions, 
  ...     ICurrentNeededInclusions)

Let's check which resources our request needs currently::

  >>> c().inclusions()
  []

Nothing yet. We now make ``y1`` needed using our simplified spelling::

  >>> y1.need()

The resource inclusion will now indeed be needed::

  >>> c().inclusions()
  [<ResourceInclusion 'b.css' in library 'foo'>, 
   <ResourceInclusion 'a.js' in library 'foo'>, 
   <ResourceInclusion 'c.js' in library 'foo'>]

In this document we already have a handy reference to ``c`` to obtain
the current needed inclusions, but that doesn't work in a larger
codebase. How do we get this reference back, for instance to obtain those
resources needed? Here is how you can obtain a utility by hand::

  >>> c_retrieved = component.getUtility(ICurrentNeededInclusions)
  >>> c_retrieved is c
  True

Let's go back to the original spelling of ``needed.need(y)``
now. While this is a bit more cumbersome to use in application code, it is
easier to read for the purposes of this document.

Multiple requirements
---------------------

In this section, we will show what happens in various scenarios where
we requiring multiple ``ResourceInclusion`` objects.

We create a new set of needed inclusions::

  >>> needed = NeededInclusions()
  >>> needed.inclusions()
  []

We need ``y1`` again::

  >>> needed.need(y1)
  >>> needed.inclusions()
  [<ResourceInclusion 'b.css' in library 'foo'>, 
   <ResourceInclusion 'a.js' in library 'foo'>, 
   <ResourceInclusion 'c.js' in library 'foo'>]

Needing the same inclusion twice won't make any difference for the
resources needed. So when we need ``y1`` again, we see no difference
in the needed resources::

  >>> needed.need(y1)
  >>> needed.inclusions()
  [<ResourceInclusion 'b.css' in library 'foo'>, 
   <ResourceInclusion 'a.js' in library 'foo'>, 
   <ResourceInclusion 'c.js' in library 'foo'>]

Needing ``x1`` or ``x2`` won't make any difference either, as ``y1``
already required ``x1`` and ``x2``::

  >>> needed.need(x1)
  >>> needed.inclusions()
  [<ResourceInclusion 'b.css' in library 'foo'>, 
   <ResourceInclusion 'a.js' in library 'foo'>, 
   <ResourceInclusion 'c.js' in library 'foo'>]
  >>> needed.need(x2)
  >>> needed.inclusions()
  [<ResourceInclusion 'b.css' in library 'foo'>, 
   <ResourceInclusion 'a.js' in library 'foo'>, 
   <ResourceInclusion 'c.js' in library 'foo'>]

Let's do it in reverse, and require the ``x1`` and ``x2`` resources
before we need those in ``y1``. Again this makes no difference::

  >>> needed = NeededInclusions()
  >>> needed.need(x1)
  >>> needed.need(x2)
  >>> needed.need(y1)
  >>> needed.inclusions()
  [<ResourceInclusion 'b.css' in library 'foo'>,
   <ResourceInclusion 'a.js' in library 'foo'>, 
   <ResourceInclusion 'c.js' in library 'foo'>]

Let's try it with more complicated dependency structures now::

  >>> needed = NeededInclusions()
  >>> a1 = ResourceInclusion(foo, 'a1.js')
  >>> a2 = ResourceInclusion(foo, 'a2.js', depends=[a1])
  >>> a3 = ResourceInclusion(foo, 'a3.js', depends=[a2])
  >>> a4 = ResourceInclusion(foo, 'a4.js', depends=[a1])
  >>> a5 = ResourceInclusion(foo, 'a5.js', depends=[a4, a3])
  >>> needed.need(a3)
  >>> needed.inclusions()
  [<ResourceInclusion 'a1.js' in library 'foo'>,
   <ResourceInclusion 'a2.js' in library 'foo'>,
   <ResourceInclusion 'a3.js' in library 'foo'>]
  >>> needed.need(a4)
  >>> needed.inclusions()
  [<ResourceInclusion 'a1.js' in library 'foo'>,
   <ResourceInclusion 'a2.js' in library 'foo'>,
   <ResourceInclusion 'a3.js' in library 'foo'>,
   <ResourceInclusion 'a4.js' in library 'foo'>]

If we reverse the requirements for ``a4`` and ``a3``, we get the following
inclusion structure, based on the order in which need was expressed::

  >>> needed = NeededInclusions()
  >>> needed.need(a4)
  >>> needed.need(a3)
  >>> needed.inclusions()
  [<ResourceInclusion 'a1.js' in library 'foo'>,
   <ResourceInclusion 'a4.js' in library 'foo'>,
   <ResourceInclusion 'a2.js' in library 'foo'>,
   <ResourceInclusion 'a3.js' in library 'foo'>]

Let's look at the order in which resources are listed when we need
something that ends up depending on everything::

  >>> a5 = ResourceInclusion(foo, 'a5.js', depends=[a4, a3])
  >>> needed = NeededInclusions()
  >>> needed.need(a5)
  >>> needed.inclusions()
  [<ResourceInclusion 'a1.js' in library 'foo'>,
   <ResourceInclusion 'a4.js' in library 'foo'>,
   <ResourceInclusion 'a2.js' in library 'foo'>,
   <ResourceInclusion 'a3.js' in library 'foo'>,
   <ResourceInclusion 'a5.js' in library 'foo'>]

When we introduce the extra inclusion of ``a3`` earlier on, we still
get a valid list of inclusions given the dependency structure, even
though the sorting order is different::

  >>> needed = NeededInclusions()
  >>> needed.need(a3)
  >>> needed.need(a5)
  >>> needed.inclusions()
  [<ResourceInclusion 'a1.js' in library 'foo'>, 
   <ResourceInclusion 'a2.js' in library 'foo'>, 
   <ResourceInclusion 'a3.js' in library 'foo'>, 
   <ResourceInclusion 'a4.js' in library 'foo'>, 
   <ResourceInclusion 'a5.js' in library 'foo'>]

Modes
-----

A resource can optionally exist in several modes, such as for instance
a minified and a debug version. Let's define a resource that exists in
two modes (a main one and a debug alternative)::

  >>> a1 = ResourceInclusion(foo, 'a.js', debug='a-debug.js')

Let's need this resource::

  >>> needed = NeededInclusions()
  >>> needed.need(a1)

By default, we get ``a.js``::

  >>> needed.inclusions()
  [<ResourceInclusion 'a.js' in library 'foo'>]

We can however also get the resource for mode ``debug`` and get
``a-debug.js``::

  >>> needed.inclusions(mode='debug')
  [<ResourceInclusion 'a-debug.js' in library 'foo'>]

Modes can also be specified fully with a resource inclusion, which allows
you to specify a different ``library`` and ``part_of`` argumnent::

  >>> a2 = ResourceInclusion(foo, 'a2.js', 
  ...                        debug=ResourceInclusion(foo, 'a2-debug.js'))
  >>> needed = NeededInclusions()
  >>> needed.need(a2)

By default we get ``a2.js``::

  >>> needed.inclusions()
  [<ResourceInclusion 'a2.js' in library 'foo'>]

We can however also get the resource for mode ``debug`` and get
``a2-debug.js``::

  >>> needed.inclusions(mode='debug')
  [<ResourceInclusion 'a2-debug.js' in library 'foo'>]

Note that modes are assumed to be identical in dependency structure;
they functionally should do the same.

"Rollups"
---------

For performance reasons it's often useful to consolidate multiple
resources into a single, larger resource, a so-called
"rollup". Multiple javascript files could for instance be offered in a
single, larger one. These consolidations can be specified when
specifying the resource::

  >>> b1 = ResourceInclusion(foo, 'b1.js', rollups=['giant.js'])
  >>> b2 = ResourceInclusion(foo, 'b2.js', rollups=['giant.js'])

If we find multiple resources that are also part of a consolidation, the
system automatically collapses them::

  >>> needed = NeededInclusions()
  >>> needed.need(b1)
  >>> needed.need(b2)

  >>> needed.inclusions()
  [<ResourceInclusion 'giant.js' in library 'foo'>]

Consolidation will not take place if only a single resource in a
consolidation is present::

  >>> needed = NeededInclusions()
  >>> needed.need(b1)
  >>> needed.inclusions()
  [<ResourceInclusion 'b1.js' in library 'foo'>]

``rollups`` can also be expressed as a list of fully specified
``ResourceInclusion``::

  >>> b3 = ResourceInclusion(foo, 'b3.js', 
  ...                        rollups=[ResourceInclusion(foo, 'giant.js')])
  >>> needed = NeededInclusions()
  >>> needed.need(b1)
  >>> needed.need(b2)
  >>> needed.need(b3)
  >>> needed.inclusions()
  [<ResourceInclusion 'giant.js' in library 'foo'>]

Consolidation also works with modes::

  >>> b4 = ResourceInclusion(foo, 'b4.js', 
  ...   rollups=['giant.js'],
  ...   debug=ResourceInclusion(foo, 'b4-debug.js', 
  ...                           rollups=['giant-debug.js']))

  >>> b5 = ResourceInclusion(foo, 'b5.js',
  ...   rollups=['giant.js'],
  ...   debug=ResourceInclusion(foo, 'b5-debug.js', 
  ...                           rollups=['giant-debug.js']))

  >>> needed = NeededInclusions()
  >>> needed.need(b4)
  >>> needed.need(b5)
  >>> needed.inclusions()
  [<ResourceInclusion 'giant.js' in library 'foo'>]
  >>> needed.inclusions(mode='debug')
  [<ResourceInclusion 'giant-debug.js' in library 'foo'>]

A resource can be part of multiple rollups. In this case the rollup that
rolls up the most resources is used::

  >>> b6 = ResourceInclusion(foo, 'b6.js',
  ...   rollups=['giant.js', 'even_bigger.js'])
  >>> b7 = ResourceInclusion(foo, 'b7.js',
  ...   rollups=['giant.js', 'even_bigger.js'])
  >>> b8 = ResourceInclusion(foo, 'b8.js',
  ...   rollups=['even_bigger.js'])
  >>> needed = NeededInclusions()
  >>> needed.need(b6)
  >>> needed.need(b7)
  >>> needed.need(b8)
  >>> needed.inclusions()
  [<ResourceInclusion 'even_bigger.js' in library 'foo'>]

Rendering resources
-------------------

Let's define some needed resource inclusions::

  >>> needed = NeededInclusions()
  >>> needed.need(y1)
  >>> needed.inclusions()
  [<ResourceInclusion 'b.css' in library 'foo'>, 
   <ResourceInclusion 'a.js' in library 'foo'>, 
   <ResourceInclusion 'c.js' in library 'foo'>]

Now let's try to render these inclusions::

  >>> print needed.render()
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.resource.interfaces.IInclusionUrl>, '')

That didn't work. In order to render an inclusion, we need to tell
``hurry.resource`` how to get the URL for a resource inclusion. 

For the purposes of this document, we define a function that renders
resources as some static URL on localhost::

  >>> def get_inclusion_url(inclusion):
  ...    return 'http://localhost/static/%s/%s' % (
  ...      inclusion.library.name, inclusion.relpath)

We should now register this function as a``IInclusionUrl`` utility so
the system can find it::

  >>> from hurry.resource.interfaces import IInclusionUrl
  >>> component.provideUtility(get_inclusion_url, 
  ...     IInclusionUrl)

Rendering the inclusions now will will result in the HTML fragment we need::

  >>> print needed.render()
  <link rel="stylesheet" type="text/css" href="http://localhost/static/foo/b.css" />
  <script type="text/javascript" src="http://localhost/static/foo/a.js"></script>
  <script type="text/javascript" src="http://localhost/static/foo/c.js"></script>

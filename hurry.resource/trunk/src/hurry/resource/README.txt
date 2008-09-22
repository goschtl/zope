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

  >>> from hurry.resource import Inclusion, ResourceSpec
  >>> x = Inclusion([ResourceSpec(foo, 'a.js'), 
  ...                ResourceSpec(foo, 'b.css')])

Let's examine the resource specs in this inclusion::

  >>> x.resources_of_ext('.css')
  [<Resource 'b.css' in library 'foo'>]

  >>> x.resources_of_ext('.js')
  [<Resource 'a.js' in library 'foo'>]

Let's now make an inclusion ``y`` that depends on ``x``, but also includes
some other resources itself::

  >>> y = Inclusion([ResourceSpec(foo, 'c.js'),
  ...                ResourceSpec(foo, 'd.css')], depends=[x])

  >>> y.resources_of_ext('.css')
  [<Resource 'b.css' in library 'foo'>, <Resource 'd.css' in library 'foo'>]

  >>> y.resources_of_ext('.js')
  [<Resource 'a.js' in library 'foo'>, <Resource 'c.js' in library 'foo'>]

As we can see the resources required by the dependency are sorted
before the resources listed in this inclusion.

Inclusion requirements
----------------------

We can also require an inclusion in a particular code path, using
``inclusion.need()``. This mean that this inclusion is added to the
inclusions that should be on the page template when it is rendered.

  >>> from hurry.resource import NeededInclusions
  >>> needed = NeededInclusions()
  >>> needed.need(y)

Let's now see what resources are needed::

  >>> needed.resources()
  [<Resource 'b.css' in library 'foo'>, 
   <Resource 'd.css' in library 'foo'>, 
   <Resource 'a.js' in library 'foo'>, 
   <Resource 'c.js' in library 'foo'>]

A simplified spelling
---------------------

Let's introduce a more convenient spelling of needs now::

  y.need()

This can be done without reference to the needed inclusions directly
as there is typically only a single set of needed inclusions that is
generated during the rendering of a page.  Let's try it::

  >>> y.need()
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.resource.interfaces.ICurrentNeededInclusions>, '')

We get an error. The system says it cannot find the component
``ICurrentNeededInclusions``. This is the component we need to define
in order to specify how the system can know what the
``INeededInclusions`` object is that the inclusion ``y`` should be
added to. So, our task is to provide a ``ICurrentNeededInclusions``
component that can give us the current needed inclusions object.

This needed inclusions should be maintained on an object that is going
to be present throughout the request/response cycle that generates the
web page that has the inclusions on them. The most obvious location on
which to maintain the needed inclusions the request object
itself. Let's introduce such a simple request object (your mileage may
vary in your own web framework)::

  >>> class Request(object):
  ...    def __init__(self):
  ...        self.needed = NeededInclusions()

We now make a request, imitating what happens during a typical
request/response cycle in a web framework::

  >>> request = Request()

We now should define a ``ICurrentNeededInclusion`` utility that knows
how to get the current needed inclusions from that request::

  >>> def currentNeededInclusions():
  ...    return request.needed

  >>> c = currentNeededInclusions

We now need to register the utility to complete plugging into our pluggability
point::

  >>> from zope import component
  >>> from hurry.resource.interfaces import ICurrentNeededInclusions
  >>> component.provideUtility(currentNeededInclusions, 
  ...     ICurrentNeededInclusions)

Okay, let's check which resources our request needs currently::

  >>> c().resources()
  []

Nothing yet.  So, let's now make ``y`` needed using our simplified
spelling::

  >>> y.need()

The resource inclusion will now indeed be needed::

  >>> c().resources()
  [<Resource 'b.css' in library 'foo'>, 
   <Resource 'd.css' in library 'foo'>, 
   <Resource 'a.js' in library 'foo'>, 
   <Resource 'c.js' in library 'foo'>]

By the way, we have a handy reference to ``c`` to get us the current
needed inclusions, but that doesn't work as soon as we lose that
reference. Here is how can get to it in general::

  >>> c_retrieved = component.getUtility(ICurrentNeededInclusions)
  >>> c_retrieved is c
  True

Multiple requirements
---------------------

Let's go back to the original spelling of ``needed.need(y)`` now. This
is a bit more cumbersome in application code, but more clear to read
in this document.

Let's create a new set of needed inclusions::

  >>> needed = NeededInclusions()
  >>> needed.resources()
  []

We need ``y`` again::

  >>> needed.need(y)
  >>> needed.resources()
  [<Resource 'b.css' in library 'foo'>, 
   <Resource 'd.css' in library 'foo'>, 
   <Resource 'a.js' in library 'foo'>, 
   <Resource 'c.js' in library 'foo'>]

Needing the same inclusion twice won't make any difference for the
resources needed. Let's try needing ``y`` againx::

  >>> needed.need(y)
  >>> needed.resources()
  [<Resource 'b.css' in library 'foo'>, 
   <Resource 'd.css' in library 'foo'>, 
   <Resource 'a.js' in library 'foo'>, 
   <Resource 'c.js' in library 'foo'>]

Needing ``x`` won't make any difference either, as ``y`` already
required ``x``::

  >>> needed.need(x)
  >>> needed.resources()
  [<Resource 'b.css' in library 'foo'>, 
   <Resource 'd.css' in library 'foo'>, 
   <Resource 'a.js' in library 'foo'>, 
   <Resource 'c.js' in library 'foo'>]

Let's do it in the reverse, and require the ``x`` resources before we
need those in ``y``. Again this makes no difference::

  >>> needed = NeededInclusions()
  >>> needed.need(x)
  >>> needed.need(y)
  >>> needed.resources()
  [<Resource 'b.css' in library 'foo'>, 
   <Resource 'd.css' in library 'foo'>, 
   <Resource 'a.js' in library 'foo'>, 
   <Resource 'c.js' in library 'foo'>]

Let's introduce an inclusion that also needs ``d.css``::

  >>> z = Inclusion([ResourceSpec(foo, 'd.css')])

We'll also require this. Again this makes no difference::

  >>> needed.need(z)
  >>> needed.resources()
  [<Resource 'b.css' in library 'foo'>, 
   <Resource 'd.css' in library 'foo'>, 
   <Resource 'a.js' in library 'foo'>, 
   <Resource 'c.js' in library 'foo'>]

We can also state the need for ``z`` first, then for ``y``::

  >>> needed = NeededInclusions()
  >>> needed.need(z)
  >>> needed.need(y)
  >>> needed.resources()
  [<Resource 'b.css' in library 'foo'>, 
   <Resource 'd.css' in library 'foo'>, 
   <Resource 'a.js' in library 'foo'>, 
   <Resource 'c.js' in library 'foo'>]

The sort order is still the same as before; inclusions with less depth
are sorted after ones with more depth.

Modes
-----

A resource can optionally exist in several modes, such as for instance
a minified and a debug version. Let's define a resource that exists in
two modes (a main one and a debug alternative)::

  >>> a1 = ResourceSpec(foo, 'a.js', debug='a-debug.js')

Let's need this resource::

  >>> inclusion = Inclusion([a1])
  >>> needed = NeededInclusions()
  >>> needed.need(inclusion)

By default, we get ``a.js``::

  >>> needed.resources()
  [<Resource 'a.js' in library 'foo'>]

We can however also get the resource for mode ``debug`` and get
``a-debug.js``::

  >>> needed.resources(mode='debug')
  [<Resource 'a-debug.js' in library 'foo'>]

Modes can also be specified fully with a resource spec, which allows
you to specify a different ``library`` and ``part_of`` argumnent::

  >>> a2 = ResourceSpec(foo, 'a2.js', debug=ResourceSpec(foo, 'a2-debug.js'))
  >>> inclusion = Inclusion([a2])
  >>> needed = NeededInclusions()
  >>> needed.need(inclusion)

By default we get ``a2.js``::

  >>> needed.resources()
  [<Resource 'a2.js' in library 'foo'>]

We can however also get the resource for mode ``debug`` and get
``a2-debug.js``::

  >>> needed.resources(mode='debug')
  [<Resource 'a2-debug.js' in library 'foo'>]

"Rollups"
---------

For performance reasons it's often useful to consolidate multiple
resources into a single, larger resource, a so-called
"rollup". Multiple javascript files could for instance be offered in a
single, larger one. These consolidations can be specified when
specifying the resource::

  >>> b1 = ResourceSpec(foo, 'b1.js', part_of=['giant.js'])
  >>> b2 = ResourceSpec(foo, 'b2.js', part_of=['giant.js'])

If we find multiple resources that are also part of a consolidation, the
system automatically collapses them::

  >>> inclusion1 = Inclusion([b1])
  >>> inclusion2 = Inclusion([b2])
  >>> needed = NeededInclusions()
  >>> needed.need(inclusion1)
  >>> needed.need(inclusion2)

  >>> needed.resources()
  [<Resource 'giant.js' in library 'foo'>]

Consolidation will not take place if only a single resource in a consolidation
is present::

  >>> needed = NeededInclusions()
  >>> needed.need(inclusion1)
  >>> needed.resources()
  [<Resource 'b1.js' in library 'foo'>]

``part_of`` can also be expressed as a list of fully specified
``ResourceSpec``::

  >>> b3 = ResourceSpec(foo, 'b3.js', part_of=[ResourceSpec(foo, 'giant.js')])
  >>> inclusion3 = Inclusion([b1, b2, b3])
  >>> needed = NeededInclusions()
  >>> needed.need(inclusion3)
  >>> needed.resources()
  [<Resource 'giant.js' in library 'foo'>]

Consolidation also can work with modes::

  >>> b4 = ResourceSpec(foo, 'b4.js', 
  ...   part_of=['giant.js'],
  ...   debug=ResourceSpec(foo, 'b4-debug.js', part_of=['giant-debug.js']))

  >>> b5 = ResourceSpec(foo, 'b5.js',
  ...   part_of=['giant.js'],
  ...   debug=ResourceSpec(foo, 'b5-debug.js', part_of=['giant-debug.js']))

  >>> inclusion4 = Inclusion([b4, b5])
  >>> needed = NeededInclusions()
  >>> needed.need(inclusion4)
  >>> needed.resources()
  [<Resource 'giant.js' in library 'foo'>]
  >>> needed.resources(mode='debug')
  [<Resource 'giant-debug.js' in library 'foo'>]

A resource can be part of multiple rollups. In this case the rollup that
rolls up the most resources is used::

  >>> b6 = ResourceSpec(foo, 'b6.js',
  ...   part_of=['giant.js', 'even_bigger.js'])
  >>> b7 = ResourceSpec(foo, 'b7.js',
  ...   part_of=['giant.js', 'even_bigger.js'])
  >>> b8 = ResourceSpec(foo, 'b8.js',
  ...   part_of=['even_bigger.js'])
  >>> inclusion5 = Inclusion([b6, b7, b8])
  >>> needed = NeededInclusions()
  >>> needed.need(inclusion5)
  >>> needed.resources()
  [<Resource 'even_bigger.js' in library 'foo'>]

Rendering resources
-------------------

Let's define some needed resource inclusions::

  >>> needed = NeededInclusions()
  >>> needed.need(y)
  >>> needed.resources()
  [<Resource 'b.css' in library 'foo'>, 
   <Resource 'd.css' in library 'foo'>, 
   <Resource 'a.js' in library 'foo'>, 
   <Resource 'c.js' in library 'foo'>]

Now let's try to render these inclusions::

  >>> print needed.render()
  Traceback (most recent call last):
    ...
  ComponentLookupError: (<InterfaceClass hurry.resource.interfaces.IResourceUrl>, '')

That didn't work. In order to render a resource, we need to tell
``hurry.resource`` how to get the URL for a resource specification. So
let's define a function that renders resources as some static URL on
localhost::

  >>> def get_resource_url(resource):
  ...    return 'http://localhost/static/%s/%s' % (
  ...      resource.library.name, resource.relpath)

We should now register this function as a``IResourceUrl`` utility so the system
can find it::

  >>> from hurry.resource.interfaces import IResourceUrl
  >>> component.provideUtility(get_resource_url, 
  ...     IResourceUrl)

Rendering the resources now will will result in the HTML fragment we need::

  >>> print needed.render()
  <link rel="stylesheet" type="text/css" href="http://localhost/static/foo/b.css" />
  <link rel="stylesheet" type="text/css" href="http://localhost/static/foo/d.css" />
  <script type="text/javascript" src="http://localhost/static/foo/a.js"></script>
  <script type="text/javascript" src="http://localhost/static/foo/c.js"></script>


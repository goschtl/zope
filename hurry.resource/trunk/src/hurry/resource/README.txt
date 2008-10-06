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
means both of them should be loaded when the page displays.

Page components may actually require a certain inclusion in order to
be functional. A widget may for instance expect a particular
Javascript library to loaded. We call this an *inclusion requirement*
of the component.

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

  >>> k1 = ResourceInclusion(foo, 'k.js', debug='k-debug.js')

Let's need this resource::

  >>> needed = NeededInclusions()
  >>> needed.need(k1)

By default, we get ``k.js``::

  >>> needed.inclusions()
  [<ResourceInclusion 'k.js' in library 'foo'>]

We can however also get the resource for mode ``debug`` and get
``k-debug.js``::

  >>> needed.inclusions(mode='debug')
  [<ResourceInclusion 'k-debug.js' in library 'foo'>]

Modes can also be specified fully with a resource inclusion, which allows
you to specify a different ``library`` argumnent::

  >>> k2 = ResourceInclusion(foo, 'k2.js', 
  ...                        debug=ResourceInclusion(foo, 'k2-debug.js'))
  >>> needed = NeededInclusions()
  >>> needed.need(k2)

By default we get ``k2.js``::

  >>> needed.inclusions()
  [<ResourceInclusion 'k2.js' in library 'foo'>]

We can however also get the resource for mode ``debug`` and get
``a2-debug.js``::

  >>> needed.inclusions(mode='debug')
  [<ResourceInclusion 'k2-debug.js' in library 'foo'>]

Note that modes are assumed to be identical in dependency structure;
they functionally should do the same.

"Rollups"
---------

For performance reasons it's often useful to consolidate multiple
resources into a single, larger resource, a so-called
"rollup". Multiple javascript files could for instance be offered in a
single, larger one. These consolidations can be specified as a
resource::

  >>> b1 = ResourceInclusion(foo, 'b1.js')
  >>> b2 = ResourceInclusion(foo, 'b2.js')
  >>> giant = ResourceInclusion(foo, 'giant.js', supersedes=[b1, b2])

If we find multiple resources that are also part of a consolidation, the
system automatically collapses them::

  >>> needed = NeededInclusions()
  >>> needed.need(b1)
  >>> needed.need(b2)

  >>> needed.inclusions()
  [<ResourceInclusion 'giant.js' in library 'foo'>]

The system will by default only consolidate exactly. That is, if only a single
resource out of two is present, the consolidation will not be triggered::

  >>> needed = NeededInclusions()
  >>> needed.need(b1)
  >>> needed.inclusions()
  [<ResourceInclusion 'b1.js' in library 'foo'>]

Let's look at this with a larger consolidation of 3 resources::

  >>> c1 = ResourceInclusion(foo, 'c1.css')
  >>> c2 = ResourceInclusion(foo, 'c2.css')
  >>> c3 = ResourceInclusion(foo, 'c3.css')
  >>> giantc = ResourceInclusion(foo, 'giantc.css', supersedes=[c1, c2, c3])
 
It will not roll up one resource::

  >>> needed = NeededInclusions()
  >>> needed.need(c1)
  >>> needed.inclusions()
  [<ResourceInclusion 'c1.css' in library 'foo'>]

Neither will it roll up two resources::

  >>> needed = NeededInclusions()
  >>> needed.need(c1)
  >>> needed.need(c2)
  >>> needed.inclusions()
  [<ResourceInclusion 'c1.css' in library 'foo'>,
   <ResourceInclusion 'c2.css' in library 'foo'>]
  
It will however roll up three resources::

  >>> needed = NeededInclusions()
  >>> needed.need(c1)
  >>> needed.need(c2)
  >>> needed.need(c3)
  >>> needed.inclusions()
  [<ResourceInclusion 'giantc.css' in library 'foo'>]

The default behavior is to play it safe: we cannot be certain that we
do not include too much if we were to include ``giantc.css`` if only
c1 and c2 are required. This is especially important with CSS
libraries: if only ``c1.css`` and ``c2.css`` are to be included in a
page, including ``giantc.css`` is not appropriate as that also
includes the content of ``c3.css``, which might override and extend
the behavior of ``c1.css`` and ``c2.css``.

The situation is sometimes different with Javascript libraries, which
can be written in such a way that a larger rollup will just include
more functions, but will not actually affect page behavior. If we have
a rollup resource that we don't mind kicking in even if part of the
requirements have been met, we can indicate this::

  >>> d1 = ResourceInclusion(foo, 'd1.js')
  >>> d2 = ResourceInclusion(foo, 'd2.js')
  >>> d3 = ResourceInclusion(foo, 'd3.js')
  >>> giantd = ResourceInclusion(foo, 'giantd.js', supersedes=[d1, d2, d3],
  ...            eager_superseder=True)

We will see ``giantd.js`` kick in even if we only require ``d1`` and
``d2``::

  >>> needed = NeededInclusions()
  >>> needed.need(d1)
  >>> needed.need(d2)
  >>> needed.inclusions()
  [<ResourceInclusion 'giantd.js' in library 'foo'>]

In fact even if we only need a single resource the eager superseder will
show up instead::

  >>> needed = NeededInclusions()
  >>> needed.need(d1)
  >>> needed.inclusions()
  [<ResourceInclusion 'giantd.js' in library 'foo'>]

If there are two potential eager superseders, the biggest one will
be taken::

  >>> d4 = ResourceInclusion(foo, 'd4.js')
  >>> giantd_bigger = ResourceInclusion(foo, 'giantd-bigger.js', 
  ...   supersedes=[d1, d2, d3, d4], eager_superseder=True)
  >>> needed = NeededInclusions()
  >>> needed.need(d1)
  >>> needed.need(d2)
  >>> needed.inclusions()
  [<ResourceInclusion 'giantd-bigger.js' in library 'foo'>]

If there is a potential non-eager superseder and an eager one, the eager one
will be taken::

  >>> giantd_noneager = ResourceInclusion(foo, 'giantd-noneager.js',
  ...   supersedes=[d1, d2, d3, d4])
  >>> needed = NeededInclusions()
  >>> needed.need(d1)
  >>> needed.need(d2)
  >>> needed.need(d3)
  >>> needed.need(d4)
  >>> needed.inclusions()
  [<ResourceInclusion 'giantd-bigger.js' in library 'foo'>]

A resource can be part of multiple rollups. In this case the rollup
that rolls up the most resources is used. So, if there are two
potential non-eager superseders, the one that rolls up the most
resources will be used::
 
  >>> e1 = ResourceInclusion(foo, 'e1.js')
  >>> e2 = ResourceInclusion(foo, 'e2.js')
  >>> e3 = ResourceInclusion(foo, 'e3.js')
  >>> giante_two = ResourceInclusion(foo, 'giante-two.js',
  ...   supersedes=[e1, e2])
  >>> giante_three = ResourceInclusion(foo, 'giante-three.js',
  ...   supersedes=[e1, e2, e3])
  >>> needed = NeededInclusions()
  >>> needed.need(e1)
  >>> needed.need(e2)
  >>> needed.need(e3)
  >>> needed.inclusions()
  [<ResourceInclusion 'giante-three.js' in library 'foo'>]

Consolidation also works with modes::

  >>> f1 = ResourceInclusion(foo, 'f1.js', debug='f1-debug.js')
  >>> f2 = ResourceInclusion(foo, 'f2.js', debug='f2-debug.js')
  >>> giantf = ResourceInclusion(foo, 'giantf.js', supersedes=[f1, f2],
  ...                            debug='giantf-debug.js')

  >>> needed = NeededInclusions()
  >>> needed.need(f1)
  >>> needed.need(f2)
  >>> needed.inclusions()
  [<ResourceInclusion 'giantf.js' in library 'foo'>]
  >>> needed.inclusions(mode='debug')
  [<ResourceInclusion 'giantf-debug.js' in library 'foo'>]

What if the rolled up resources have no mode but the superseding resource
does? In this case the superseding resource's mode has no meaning, so
modes have no effect::

  >>> g1 = ResourceInclusion(foo, 'g1.js')
  >>> g2 = ResourceInclusion(foo, 'g2.js')
  >>> giantg = ResourceInclusion(foo, 'giantg.js', supersedes=[g1, g2],
  ...                            debug='giantg-debug.js')
  >>> needed = NeededInclusions()
  >>> needed.need(g1)
  >>> needed.need(g2)
  >>> needed.inclusions()
  [<ResourceInclusion 'giantg.js' in library 'foo'>]
  >>> needed.inclusions(mode='debug')
  [<ResourceInclusion 'giantg.js' in library 'foo'>]

What if the rolled up resources have a mode but the superseding resource
does not? Let's look at that scenario::

  >>> h1 = ResourceInclusion(foo, 'h1.js', debug='h1-debug.js')
  >>> h2 = ResourceInclusion(foo, 'h2.js', debug='h2-debug.js')
  >>> gianth = ResourceInclusion(foo, 'gianth.js', supersedes=[h1, h2])
  >>> needed = NeededInclusions()
  >>> needed.need(h1)
  >>> needed.need(h2)
  >>> needed.inclusions()
  [<ResourceInclusion 'gianth.js' in library 'foo'>]

Since there is no superseder for the debug mode, we will get the two 
resources, not rolled up::

  >>> needed.inclusions(mode='debug')
  [<ResourceInclusion 'h1-debug.js' in library 'foo'>,
   <ResourceInclusion 'h2-debug.js' in library 'foo'>]

XXX superseding along with dependencies...

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
  TypeError: ('Could not adapt', <hurry.resource.core.Library object at ...>, <InterfaceClass hurry.resource.interfaces.ILibraryUrl>)

That didn't work. In order to render an inclusion, we need to tell
``hurry.resource`` how to get the URL for a resource inclusion. We
already know the relative URL, so we need to specify how to get a URL
to the library itself that the relative URL can be added to.

For the purposes of this document, we define a function that renders
resources as some static URL on localhost::

  >>> def get_library_url(library):
  ...    return 'http://localhost/static/%s' % library.name

We should now register this function as a``ILibrarUrl`` adapter for
``Library`` so the system can find it::

  >>> from hurry.resource.interfaces import ILibraryUrl
  >>> component.provideAdapter(
  ...     factory=get_library_url,
  ...     adapts=(Library,), 
  ...     provides=ILibraryUrl)

Rendering the inclusions now will will result in the HTML fragment we need::

  >>> print needed.render()
  <link rel="stylesheet" type="text/css" href="http://localhost/static/foo/b.css" />
  <script type="text/javascript" src="http://localhost/static/foo/a.js"></script>
  <script type="text/javascript" src="http://localhost/static/foo/c.js"></script>

Generating resource code
------------------------

Sometimes it is useful to generate code that expresses a complex
resource dependency structure. One example of that is in
``hurry.yui``. We can the ``generate_cod`` function to render resource
inclusions::

  >>> i1 = ResourceInclusion(foo, 'i1.js')
  >>> i2 = ResourceInclusion(foo, 'i2.js', depends=[i1])
  >>> i3 = ResourceInclusion(foo, 'i3.js', depends=[i2])
  >>> i4 = ResourceInclusion(foo, 'i4.js', depends=[i1])
  >>> i5 = ResourceInclusion(foo, 'i5.js', depends=[i4, i3])

  >>> from hurry.resource import generate_code
  >>> print generate_code(i1=i1, i2=i2, i3=i3, i4=i4, i5=i5)
  from hurry.resource import Library, ResourceInclusion
  <BLANKLINE>
  foo = Library('foo')
  <BLANKLINE>
  i1 = ResourceInclusion(foo, 'i1.js')
  i2 = ResourceInclusion(foo, 'i2.js', depends=[i1])
  i3 = ResourceInclusion(foo, 'i3.js', depends=[i2])
  i4 = ResourceInclusion(foo, 'i4.js', depends=[i1])
  i5 = ResourceInclusion(foo, 'i5.js', depends=[i4, i3])

Let's look at a more complicated example with modes and superseders::

  >>> j1 = ResourceInclusion(foo, 'j1.js', debug='j1-debug.js')
  >>> j2 = ResourceInclusion(foo, 'j2.js', debug='j2-debug.js')
  >>> giantj = ResourceInclusion(foo, 'giantj.js', supersedes=[j1, j2],
  ...                            debug='giantj-debug.js')

  >>> print generate_code(j1=j1, j2=j2, giantj=giantj)
  from hurry.resource import Library, ResourceInclusion
  <BLANKLINE>
  foo = Library('foo')
  <BLANKLINE>
  j1 = ResourceInclusion(foo, 'j1.js', debug='j1-debug.js')
  j2 = ResourceInclusion(foo, 'j2.js', debug='j2-debug.js')
  giantj = ResourceInclusion(foo, 'giantj.js', supersedes=[j1, j2], debug='giantj-debug.js')

We can control the name the inclusion will get in the source code by
using keyword parameters::

  >>> print generate_code(hoi=i1)
  from hurry.resource import Library, ResourceInclusion
  <BLANKLINE>
  foo = Library('foo')
  <BLANKLINE>
  hoi = ResourceInclusion(foo, 'i1.js')

  >>> print generate_code(hoi=i1, i2=i2)
  from hurry.resource import Library, ResourceInclusion
  <BLANKLINE>
  foo = Library('foo')
  <BLANKLINE>
  hoi = ResourceInclusion(foo, 'i1.js')
  i2 = ResourceInclusion(foo, 'i2.js', depends=[hoi])

Sorting inclusions by dependency
--------------------------------

This is more a footnote than something that you should be concerned
about. In case assumptions in this library are wrong or there are
other reasons you would like to sort resource inclusions that come in
some arbitrary order into one where the dependency relation makes
sense, you can use ``sort_inclusions_topological``::

  >>> from hurry.resource import sort_inclusions_topological

Let's make a list of resource inclusions not sorted by dependency::

  >>> i = [a5, a3, a1, a2, a4]
  >>> sort_inclusions_topological(i)
  [<ResourceInclusion 'a1.js' in library 'foo'>, 
   <ResourceInclusion 'a4.js' in library 'foo'>, 
   <ResourceInclusion 'a2.js' in library 'foo'>, 
   <ResourceInclusion 'a3.js' in library 'foo'>, 
   <ResourceInclusion 'a5.js' in library 'foo'>]

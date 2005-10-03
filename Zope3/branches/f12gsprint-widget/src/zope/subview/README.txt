XXX The intent is to make this a test, as usual.

===============
Subview package
===============

The subview package provides a core set of interfaces for views that operate
within other views, and some small base implementations.

Views within other views include form widgets, JSR-168-type portlets, page
composition portlets a la CPSskins, etc.

This package is currently pertinent to browser views.  It may be expanded to
other types of subviews if we ever gain experience with them.  It will need
to be refactored at that time, if so.

The goals of the core interface include the following.

- Establish a standard pattern for subviews for easier interoperability.
  Specifically, this package

  * separates calculating subview state from rendering the subview; and
  
  * defines the composition and use of prefixes.

- Enable interoperable rich client-side approaches among subviews.  In
  particular, the package contemplates two common use cases:
  
  * AJAX, so that client code from a rendered subview may directly address
    the Python subview on the server for a given AJAX call; and

  * drag and drop, so that unrelated subviews can allow items to be dragged
    and dropped between them, and enabled via site configuration.

- Enable subview persistence, so that subviews may be stashed away
  temporarily and then redrawn.  For instance, 
  
  * forms may need to defer to another form, perhaps adding a desired value to
    a source used on the original form, before returning;

  * wizards may simply persist views in a session as they gather information;

  * form file widgets on persisted views may simply persist references to
    gathered files as they validate and communicate with the user;

  * one subview of many may be expanded, hiding all others, across
    transactions; and then changed to a normal size again, revealing original
    subviews;

  * views may simply wish to persist, like portlets; and
  
  * AJAX calls may benefit from interacting with persistent views.

We will look at each of the three main features in turn: a standard pattern,
rich-client support, and subview persistence.

------------------
A Standard Pattern
------------------

Based on lessons learned from the Zope 3 form code and from an in-house Zope
Corporation JSR-168-like portlet system, the subview interfaces encapsulate
current best practices.  Some of these drive the other two main package goals,
but two others bear highlighting.

First, subviews often require an explicit delineation of
initialization--calculating the state for the subview--and rendering. 
Following the pattern of the zope.formlib.interfaces.ISubPage interface, the
subview interface separates this into update and render.  All subviews should
be updated before any are rendered.  All analysis of the request and
setting of subview state should happen in update, while all rendering (for the
response) should happen in render.  This is essential to supporting subviews
that may affect other subviews: otherwise update bugs, in which the underlying
data changed as expected but it was not drawn to screen because it was out of
order, are frequent.

For our examples, note that we are making no assumptions about the rendering
output other than it being non-None.

    >>> container = SubviewContainer()
    >>> s = Subview()
    >>> container._add('test', s) # !!! _add is not in API
    >>> container.update() # this should also initialize the subview
    >>> s.render() is not None # should output the subview rendering
    True

    >>> container = SubviewContainer()
    >>> nested = NestedSubview()
    >>> container._add('inter', nested) # !!! _add is not in API
    >>> s = Subview()
    >>> nested._add('test', s) # !!! _add is not in API
    >>> container.update() # should cascade initialize down
    >>> nested.render() is not None
    True
    >>> s.render() is not None
    True

Second, subviews have a prefix which, along with a final dot, is the namespace
with which the subview should prefix all names and identifiers.  The prefix
may change between the update and render calls, which highlights another
important aspect of parsing the request only in initialize:
stored values should not rely on the current prefix.

name is the name for this view in the subview container.  parent is the
immediate subview container of the subview.  They are both only supposed to be
accurate after update is called.  The prefix of a subview is calculated by
combining the prefix of the parent with a dot and the name of the subview.
The prefix itself, as a name without a following dotted element, is reserved
for use in the immediate subview container.  The prefix of a subview container
(that is not itself a subview) may be set directly.

    >>> nested.parent is container
    True
    >>> s.parent is nested
    True
    >>> nested.name
    'inter'
    >>> nested.prefix
    'inter'
    >>> s.name
    'test'
    >>> s.prefix
    'inter.test'
    >>> container.prefix = 'cont'
    >>> nested.prefix
    'cont.inter'
    >>> s.prefix
    'cont.inter.test'
    >>> nested.name = 'nest'
    >>> nested.prefix
    'cont.nest'
    >>> s.prefix
    'cont.nest.test'
    >>> nested.render() is not None
    True
    >>> s.render() is not None
    True

To emphasize, the prefix should be used to calculate state during update,
and to render during render; do not assume that the prefix will be the same
across the calls.  To reiterate, the prefix should be used as a namespace--a
prefix--for identifiers within the subview, but the prefix itself, without a
following '.', is reserved for use by the container, for a purpose described
below.

The fact that the prefix is calculated from the parent and the name, rather
than set in toto, is another part of this best practice, different from
previous interfaces.  It reduces the chance for bugs when moving subviews
among parents.

    >>> s.prefix
    'cont.nest.test'
    >>> s.parent = container
    >>> s.parent is container
    True
    >>> s.prefix
    'cont.test'

It's also worth noting that concurrency issues suggest that subview containers
should be very wary of reassigning names, and particularly of reusing names
for different subviews.  For instance, imagine a subview container with two
subviews.  The programmer decides to name them with their order, '0' and '1'
hypothetically.  A first user looks at the page and begins to work with the
second subview.  Meanwhile, a second user deletes the first subview ('0').  If
the names are simply based on order, then now what was subview '1' is subview
'0'--if the first user tries to interact with the system, the rug will have
been pulled out, because the subview appears to no longer exist.  Further
imagine that the second user added a completely new subview, now named '1'. 
If the first user submits now, then information intended for one subview will
be sent to another.

This hints at another problem: what should we do when the parent of the subview
changes, in a similar story involving concurreny?  This is a thornier problem
for the applications that must address it.  If your application must consider
this problem, here are two possible solutions.

- Use a calculated prefix for the object that is not based on hierarchy, as
  described in ISubview.prefix.

- Don't do it.  Make a shallow static subview hierarchy and arrange subviews
  using a different mechanism (a smarter main view, for instance).

A separation between update and render and a prefix model are two important
best practices used in the subview package.  Other best practices are
discussed in the remaining two sections.

---------------------------
Rich-Client Browser Support
---------------------------

As discussed in the introduction, this package contemplates support for two
rich-client approaches in subviews: AJAX and drag and
drop.

AJAX
----

The primary AJAX use case is that a subview should be able to communicate
directly with itself.  This requires that there be a standard, agreed-upon way to
address a subview via a URL.  This package offers a traverser that uses a
traversal namespace of ++subview++.  It can be traversed with a subview's 
prefix, and will offer up registered names of the subview for following
traversal.  For instance, if a view is served at 
http://localhost/foo/index.html, and it has a nested subview with a prefix of
bar.baz.bing, and it has a method named getWeather that it wants to address,
then this might work:

    def getWeather(self, location)...

    >>> zcml("<configure><page name='getWeather' ...></configure>")
    >>> browser.open(
    ... 'http://localhost/foo/index.html/++subview++bar.baz.bing/getWeather?location=Fredericksburg')
    >>> print browser.contents
    'The weather is lovely and cool right now.'

This approach might also allow direct submission to a subview, if desired,
which could return an html snippet to replace the subview.  This would remove
some of the necessity for our reliance on the super-form approach,
which was developed to maintain state in the browser for multiple sub-forms
when only one form was submitted.

    XXX example

Subview containers are required to make a div around the subview output with an
id of the subview prefix and a class of 'zope.subview'.  This div can be used
to replace contents of the subview on the basis of the form submission, if
desired.  The div also has another use: an identifier for drag and drop,
discussed next.

Drag and Drop
-------------

Generic drag and drop between subviews can enable a number of very exciting
scenarios.  For instance, imagine a subview that provides a list of a user's
most-used coworkers.  Selecting the user in a form might involve dragging the
coworker from one subview into a widget, that is itself a subview.  Sending the
user a message might involve dragging a document in one subview to a user in
another.  A complicated assembly process might be aided by a subview that
maintained a clipboard, into which components could be dragged from multiple
parts of the site while dragging, and out of which components could be dragged
into assembly.

If you find these stories exciting and compelling, this package establishes a
tested and easy pattern that makes them possible.  If you don't find them
compelling, you'll be happy to know that opting out is trivial.  The only
shared requirement for all is that subview containers place a div around each
subview's output with an id of the subview's prefix, and a class of 
'zope.subview'.  If you are not interested in drag and drop, you can skip to
the next section now ("Subview Persistence").  That's it.

If you want to use drag and drop, see draganddrop.txt for more information.

-------------------
Subview Persistence
-------------------

As indicated in the introduction to this file, subview persistence has many
use cases.  The solution taken by the ISubview interface is simple, at least
conceptually: make it implement standard ZODB persistence.  If the object is
not attached to a persistent object, it will be thrown away in normal garbage
collection.  If code wishes to persist the subview, simply attach it to a
persistent data structure already part of the ZODB, such as a principal
annotation.

Unfortunately, the simple solution is not quite so simple in implementation. 
If a subview is persisted, it does have some unusual requirements.  The
majority of these are handled by the default base class.

First, requests and non-IPersistent parents must not be persisted. The parent
may not be persisted because it may be a transient view, not designed for
persistence; the request is also not designed for persistence, and the next
time the view is used it will probably need to be associated with the current
request, not the original one.  This constraint is met in the default base
implementation by always getting the request from the interaction, instead of
making it an actual attribute; and by storing non-persistent parents as
request annotations.

    >>> from zope.publisher.interfaces import IRequest
    >>> IRequest.providedBy(Subview().request)
    True
    >>> from zope.persistent.interfaces import IPersistent
    >>> IPersistent.providedBy(s)
    True
    >>> IPersistent.providedBy(nested)
    True
    >>> IPersistent.providedBy(container)
    False
    >>> nested.parent is container
    True
    >>> import cPickle
    >>> getattr(cPickle.loads(cPickle.dumps(nested)), 'parent', None) is None
    True
    >>> s.parent = nested
    >>> cPickle.loads(cPickle.dumps(s)).parent is nested
    True
    # XXX maybe do this with a real app, in a functional test wrapper...

Second, when persisted subviews are used again, they must have the correct
parent and request.  The default implementation gets the request from the
thread-local security interaction, so only re-updating the subview with the
current parent should be necessary.  The update method should be careful to
accomodate new system state, rather than make assumptions.  Note that a subview
should always have 'update' called whenever it is used with a new request,
before 'render' is called.  Note that the default implementation also defers
its context to the parent view, so that may not need to be reset.

    # XXX end transaction, start a new one with a new request, and call update
    # and render on 's'

Last, if the subview is shared among various users, then essentially spurious
but very annoying conflict errors may occur when parents (and requests, if the
default implementation is not used) are tacked on to the subview.  Each
attribute assignment of 'parent' will tag the view as needing to be persisted,
and thus cause the ZODB to raise a ConflictError if multiple users set the
attribute--even though the attribute is not persisted!  Persisted subviews
sometimes store per-principal customization information in principal
annotations; this approach might also be used to store the parent, but then
again the value should not actually be persisted.  The parent might also be
stored in a request annotation: this might be the easiest approach, since the
reference will naturally have the correct lifespan: this is taken by the
default implementation.  A third approach might be to write a __getstate__ that
does not include parent or request along with conflict resolution
code that ignores 'imaginary' changes like the ones to parent and request
(as a reminder to the writer of this file :-), that's
"def _p_resolveConflict(self, oldState, savedState, newState):...").

    # make another DB copy of s, make a 'conflict' by setting parent, and
    # show that transaction has no error. XXX

It is essential for interoperability that subviews do not opt-out of the
requirements for this part of the interface.  Otherwise, their subviews will
break intermediate persistent subviews in unpleasant ways (e.g., causing
database exceptions when a transaction commits, etc.).  Hopefully the shared
base class will alleviate the annoyance for individual subview writers.

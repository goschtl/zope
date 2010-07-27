Concepts and Technologies
=========================

Concepts
--------

Interface
~~~~~~~~~

Interfaces are objects that specify (document) the external behavior
of objects that "provide" them.  An interface specifies behavior
through:

- Informal documentation in a doc string

- Attribute definitions

- Invariants, which are conditions that must hold for objects that
  provide the interface

Some of the motivations for using interfaces are:

- Avoid monolithic design by developing small, exchangeable pieces

- Model external responsibility, functionality, and behavior

- Establish contracts between pieces of functionality

- Document the API

Zope Component Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main idea in the Zope Component Architecture is the use of
components, rather than multiple-inheritance for managing complexity.

Zope Component Architecture is about how to create reusable
components, but not reusable components itself.

A component is a reusable object with introspectable interfaces.
Also components are cohesive and decoupled objects.  A component
provides an interface implemented in a class.  It doesn't matter how
a component is implemented, the important part is that it complies
with its interface contracts.  An interface is an object that
describes how you work with a particular component.  Using Zope
component architecture we can spread the complexity of systems over
multiple cooperating components.  Zope component architecture help us
to create two basic kinds of components, adapters and utilities.

Event
~~~~~

Events are objects that represent something happening in a system.
They are used to extend processing by providing processing plug
points.  The `zope.event <http://pypi.python.org/pypi/zope.event>`_
provides the basic event publishing system.  The ``zope.event``
package also provides a very simple event-dispatching system on which
more sophisticated event dispatching systems can be built.  For
example, a type-based event dispatching system that builds on
``zope.event`` can be found in zope.component.

Adapter
~~~~~~~

.. based on zope-cookbook.org

Summary: Adapter takes the Interface of an existing component and
adapts it to provide another Interface.

When applications gets bigger, there is a side effect on the code,
called the spaggethi effect: interactions between classes can lead to
unwanted dependencies and the code turns into a monolithic block.

Adapters provides a way to prevent from this, by implementing the
Liskov substitution principle.

Adapters provide a cooperation mechanism between any given object and
a particular context, using interfaces.  They allow an abritary type
of class to be compatible with a given interface, by giving a
compatibility layer.

This mechanism is used in systems like Microsoft COM's QueryAdapter,
and let the developer gathers objects in a specific functional
context.  This also known as glue code.

Adapters provides several advantages:

* They can gather class instances in contexts they where not
  implemented for, without having to change their code or make them
  depend on each other.

* They offer a smooth way to gather generic features, that can be
  applied on several kind of classes.

Adapters can be seen as a formalized duck typing and where proposed
some years ago in PEP 246.  There are also Python implementations of
it, like PyProtocols.

Utility
~~~~~~~

Utility components are components that serve only one specific
function, and are not designed to act on another component.  A good
analogy for Python programmers are functions and methods.  Utility
components, like Python functions, are standalone objects that do not
need any other objects to do their work.  Adapter components, like
Python methods, require another object to work upon.

Utility components will mostly be used for simple, throw-away
components that serve one simple task, like an XML parser.  Sometimes
it would be useful to register an object which is not adapting
anything.  Database connection, XML parser, object returning unique
Ids etc. are examples of these kinds of objects.  These kind of
components provided by the ZCA are called utility components.

Utilities are just objects that provide an interface and that are
looked up by an interface and a name.  This approach creates a global
registry by which instances can be registered and accessed by
different parts of your application, with no need to pass the
instances around as parameters.

Subscriber
~~~~~~~~~~

Unlike regular adapters, subscription adapters (subscriber) are used
when we want all of the adapters that adapt an object to a particular
interface.  Subscription adapter is also known as subscriber.

Handler
~~~~~~~

Handlers are subscription adapter factories that don't produce
anything.  They do all of their work when called.  Handlers are
typically used to handle events.  Handlers are also known as event
subscribers or event subscription adapters.

Event subscribers are different from other subscription adapters in
that the caller of event subscribers doesn't expect to interact with
them in any direct way.  For example, an event publisher doesn't
expect to get any return value.  Because subscribers don't need to
provide an API to their callers, it is more natural to define them
with functions, rather than classes.

Component Registry
~~~~~~~~~~~~~~~~~~

Registries keep the list of which components are available, which
interface they provide, which interface(s) they possibly adapt, along
with an optional registration name.  The ``zope.component`` package
implements a global component registry.  The ``zope.site`` package
provides a local and persistent component registry called site
manager, so that one can register local utilities and adapters.

Object Publishing
~~~~~~~~~~~~~~~~~

BlueBream puts your objects on the web.  This is called object
publishing.  One of BlueBream's unique characteristics is the way it
allows you to walk up to your objects and call methods on them with
simple URLs.  In addition to HTTP, BlueBream makes your objects
available to other network protocols including FTP, WebDAV and
XML-RPC.

View
~~~~

.. based on: http://wiki.zope.org/zope3/WhatIsAViewWhatAreContextAndRequest

**Views** provide a connection between an **external actor** and an **object**.

A View is typically a display component. Views are typically
reponsible for creating HTML.  Views can directly return HTML, but
will often supply presentational logic and processed data to a Zope
Page Template, which then contains the HTML.

Web developers will normally deal with a specialized View called a
BrowserView.  This is just a View that is made for a web browser, as
BlueBream can also provide Views for other protocols, such as FTP or
WebDAV.  In a BrowserView, the **external actor** is a web browser
**request**, and the **object** that the view connects is looked up
using traversal and is called the **context**.  Because the Web is
the predominant focus of most Zope developers, often the term View is
assumed to be a BrowserView.

The constructor for a BrowserView looks like this::

	class BrowserView(Location):
	    implements(IBrowserView)

	    def __init__(self, context, request):
	        self.context = context
	        self.request = request


**Context** is the object that the View is acting upon.  Often
context will be a Content or Model object, but it may also be a
Container or Site object or any object that Zope can publish.

**Request** is an HTTP Request.  If the View is a BrowserView, the
Request will have a form attribute where all form data is already
marshalled for the programmer.

Consider the URL
http://localhost:8080/your-id/a-todo-list/get-cat-food.  In
BlueBream, ``your-id`` would be a Container component that also
provided a IHomeFolder interface, ``a-todo-list`` would be a To-Do
Container component that also provided a IToDoList interaface, and
``get-cat-food`` would be a ToDo-Item Content or Model component that
also provided a IToDoItem interface.  If you entered the URL
http://localhost:8080/your-id/a-todo-list/get-cat-food into your web
browser, then **context** would be an object that provided the
IToDoItem interface, while **request** would be an object that
represented the web browser request for that web page. However, if
the URL was just http://localhost:8080/your-id/ then **context**
would be an object that represented your home folder.

You can look-up a View programmatically with a query::

    view = component.queryMultiAdapter((object, request), name='index')

For more reading on Views, there is a section about them in the Plone
Core Developer Reference that provides information on how BlueBream
Views are being used in Plone:
http://plone.org/documentation/manual/plone-developer-reference/patterns/views

Content Object
~~~~~~~~~~~~~~

Content obejcts are objects with a user visisble view. 

If an **interface** provides ``zope.app.content.interfaces.IContentType``
interface type, then all objects providing the **interface** are considered
content objects.

Container
~~~~~~~~~

Containers are content objects which hold content objects.

Schema
~~~~~~

Schemas are just an extension to interfaces and therefore depend on
the ``zope.interface`` package.  Fields in schemas are equivalent to
methods in interfaces.  Both are complementary to each other, since
they describe different aspects of an object.  The methods of an
interface describe the functionality of a component, while the
schema’s fields represent the state.

Schemas provide:

1. Full specification of properties on an API level
2. Data input validation and conversion
3. Automated GUI form generation (mainly for the Web browser)

Widget
~~~~~~

The views of schema fields are called widgets.  Widgets responsible
for data display and conversion in their specific presentation type.
Currently widgets exist mainly for HTML (the Web browser).

Widgets are separated into two groups, display and input widgets.
Display widgets are often very simply and only show a text
representation of the Python object.  The input widgets, however, are
more complex and display a greater variety of choices.

Layer
~~~~~

- Define the “feel” of a site
- Contain presentation logic
- Common artifacts: pages, content providers, viewlet managers, and viewlets
- Developed by BlueBream application developers

Skin
~~~~

- Define the “look” of a site
- Common artifacts: templates and resources (CSS, Javascript, etc.)
- Use layers to retrieve the data for templates
- Developed by HTML and Graphic Designer/Scripter

Technically, skins are interfaces inherited from a special interface
called ``IDefaultBrowserLayer``.  The ``IDefaultBrowserLayer`` is
defined in ``zope.publisher.interfaces.browser`` module.  You can
also inherit from an already existing skin.  It is also important to
register the skin interface type as ``IBrowserSkinType``.  Skins are
directly provided by a request.

.. note:: Layers versus skins

    - Both are implemented as interfaces

    - BlueBream does not differentiate between the two

    - In fact, the distinction of layers defining the “feel” and
      skins the “look” is a convention. You may not want to follow
      the convention, if it is too abstract for you, but if you are
      developing application with multiple look and feel, I strongly
      suggest using this convention, since it cleanly separates
      concerns.

    - Both support inheritance/acquisition


Annotation
~~~~~~~~~~

Every object that comes with BlueBream and can have some sort of
annotation, uses attribute annotations.  Attribute annotations store
the annotation data directly in the objects.  This implementation
works fine as long as the object is persistent and is stored in the
ZODB.  But what if you have SQL-based objects, such as in
relational-to-object mapping solutions? Storing annotations on the
attribute of the object would certainly not work.  In these scenarios
it becomes necessary to implement a custom annotations
implementation.

First, there exists an interface named ``IAnnotatable``.  By
providing this interface, an object declares that it is possible to
store annotations for itself.

However, ``IAnnotable`` is too general, since it does not specify how
the annotation can be stored and should therefore never be provided
directly.  One should never assume that one method works for all
possible objects.

BlueBream comes by default with an ``IAttributeAnnotatable``
interface that allows you to store the annotations in the attribute
``__annotations__`` on the object itself.  This works well for any
object whose instances are stored in the ZODB.

As second part to the equation we have the ``IAnnotations``
interface, which provides a simple mapping API (i.e. dictionary-like)
that allows you to look up annotation data using a unique key.  This
interface is commonly implemented as an adapter requiring
IAnnotatable and providing IAnnotations.  Thus we need to provide an
implementation for ``IAnnotations`` to have our own annotations
storage mechanism.

For ``IAttributeAnnotable`` we have an ``AttributeAnnotations``
adapter.  Note that by definition ``IAnnotations`` extends
``IAnnotable``, since an ``IAnnotation`` can always adapt to itself.

Another important aspect about annotations is the key (unique id)
that is being used in the mapping.  Since annotations may contain a
large amount of data, it is important to choose keys in a way that
they will always be unique.  The simplest way to ensure this is to
include the package name in the key.  So for dublin core meta data,
for example, instead of using ``ZopeDublinCore`` as the key one
should use ``zope.app.dublincore.ZopeDublinCore``.  Some people also
use a URI-based namespace notation:
``http://namespace.zope.org/dublincore/ZopeDublinCore/1.0.``

Content Provider
~~~~~~~~~~~~~~~~

Content Provider is a term from the Java world that refers to
components that can provide HTML content.  It means nothing more! How
the content is found and returned is totally up to the
implementation.  The BlueBream touch to the concept is that content
providers are multi-adapters that are looked up by the context,
request (and thus the layer/skin), and view they are displayed in.

The second important concept of content providers are their two-phase
rendering design.  In the first phase the state of the content
provider is prepared and, if applicable, any data, the provider is
responsible for, is updated.

Viewlet
~~~~~~~

Viewlets provide a generic framework for building pluggable user
interfaces.

Technologies
------------

ZODB
~~~~

The Zope Object Database provides an object-oriented database for
Python that provides a high-degree of transparency.  Applications can
take advantage of object database features with few, if any, changes
to application logic.  ZODB includes features such as a pluggable
storage interface, rich transaction support, and undo.

Python programs are written with the object-oriented paradigm.  You
use objects that reference each other freely and can be of any form
and shape: no object has to adhere to a specific schema and can hold
arbitrary information.

Storing those objects in relational databases requires you to give up
on the freedom of reference and schema.  The constraints of the
relational model reduces your ability to write object-oriented code.

The ZODB is a native object database, that stores your objects while
allowing you to work with any paradigms that can be expressed in
Python.  Thereby your code becomes simpler, more robust and easier to
understand.

Also, there is no gap between the database and your program: no glue
code to write, no mappings to configure.  Have a look at the tutorial
to see, how easy it is.

Some of the features that ZODB brings to you:

- Transparent persistence for Python objects
- Full ACID-compatible transaction support (including savepoints)
- History/undo ability
- Efficient support for binary large objects (BLOBs)
- Pluggable storages
- Scalable architecture

ZCML
~~~~

.. based on http://worldcookery.com/files/ploneconf05-five/step2.html

BlueBream separates all the policy from the actual code and moves it
out to separate configuration files.  The Zope Configuration Markup
Language (ZCML), the XML-based configuration language that is used
for this, is tailored to do component registration and security
declarations, for the most part.  By enabling or disabling certain
components in ZCML, you can configure certain policies of the overall
application.  If you don't enable it explicitly, it will not be
found.

WSGI
~~~~

:term:`WSGI` is the Web Server Gateway Interface.  It is a
specification for web servers and application servers to communicate
with web applications (though it can also be used for more than
that).  It is a Python standard, described in detail in `PEP 333
<http://www.python.org/dev/peps/pep-0333/>`_.

PasteScript
~~~~~~~~~~~

PasteScript is an external package created by Ian Bicking.

PasteScript is a framework for defining commands.  It comes with a
few commands out of the box, like ``paster serve`` and ``paster
create``.

The ``paster serve`` command loads and serves a WSGI application
defined in a Paste Deploy config file.  The ``paster create`` command
creates directory layout for packages from a template.

PasteDeploy
~~~~~~~~~~~

PasteDeploy is an external package created by Ian Bicking.  

PasteDeploy is a system for loading and configuring WSGI applications
and servers.  PasteDeploy create a WSGI app as specified in the
configuration file.  The INI format of configuration file is
specified by PasteDeploy.

From the PasteDeploy site:

Paste Deployment is a system for finding and configuring WSGI
applications and servers.  For WSGI application consumers it provides
a single, simple function (loadapp) for loading a WSGI application
from a configuration file or a Python Egg.  For WSGI application
providers it only asks for a single, simple entry point to your
application, so that application users don’t need to be exposed to
the implementation details of your application.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>

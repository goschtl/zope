Overview
========

The ``zc.publication`` package eases development of WSGI applications
using the Zope Toolkit publishing frameworks.  Leveraging the Zope
Toolkit publication frameworks, ``zc.publication`` provides:

- object traversal from a root object,
- mapping of requests to transactions,
- a *optional* security protection system [#protection]_
  (using sercurity proxies),
- *optional* authentication during traversal to allow multiple
   authentication domains,
- events to notify applications of key pooints in the request lidecycle,
- error handling with
  - application-provided error views,
  - application-pluggable error logging,
  - request retry to handle conflicting transactions,

With ``zc.publication``, these features can largely be ignored until
they are needed.

Getting Started: Hello World
============================

Let's start with among the simplest applications you can create, once
that provides a single web resource.  We'll create a web resource that
simply outputs the text, "Hello World!", using the module ``hello.py``::

    def hello():
        return """<html><body>
        Hello World!
        </body></html>
        """

.. -> src

    >>> update_module('hello', src)

To turn this into a web application, we'll use ``zc.publication``.
``zc.publication`` builds on ``zope.publisher`` and Paste Deployment.

Paste Deployment is used to assemble a web server from WSGI
components, including, at a minimum, a application component and a
server.  See the Paste Deployment documentation for more information.

We create a Paste Deployment configuration file, ``hello.ini``::

    [app:main]
    use = egg:zc.publication
    root = hello:lambda request: hello
    loggers =
      <logger>
         level INFO
         <logfile>
           path STDOUT
         </logfile>
      </logger>

    [server:main]
    use = egg:Paste#http
    port = 8080

.. -> src

    >>> open('hello.ini', 'w').write(src)
    >>> app = testapp('hello.ini')


The configuration file defines a web server using an application
component and a server.  The ``server:main`` section defines the web
server to use.  Here we use an HTTP server provides by the Paste egg,
running on port 8080.

The ``app.main`` section defines the application.  The use option
specifies a Paste Deployment application factory. Here we use the
factory provided by zc.publication.  The ``zc.publication``
application factory accepts a number of options:

root
   A module and expression, of the form ``module:expression`` that
   specifies a factory that takes a request and returns the root object for
   traversal

zcml
   Zope Configuration Markup (ZCML) source.

   If this option isn't specified, the configuration provided by
   ``zc.publication`` is used.

proxy
   A module and expression, of the form ``module:expression`` a
   security proxy function

   If this option is ommitted, then no proxies are used.  To use the
   standard Zope Toolkit security proxies, use
   ``zope.security.checker.ProxyFactory``.

In ``hello.ini``, we only used the root option.  We specified a
root-object factory using a lambda that just returned the hello function.

With this example, we can visit the URL::

   http://localhost:8080/

.. -> url strip

and get::

   <html><body>
       Hello World!
       </body></html>

.. -> expected strip

    >>> app.get(url, status=200).body.strip() == expected
    True

Views
=====

Another way to make resources available is using views.  Views display
content objects.  Lets rewrite our hello resource as a view::

    class Hello(object):

        def __init__(self, context, request):
            pass

        def __call__(self):
            return """<html><body>
            Hello World!
            </body></html>
            """

.. -> src

    >>> update_module('hello', src)

A view adapts a context, typically a content object of some sort, and
a request and provides a call method to generate a page.

We register views aith ZCML. Let's change our configuration file::

    [app:main]
    use = egg:zc.publication
    zcml =
       <configure xmlns="http://namespaces.zope.org/zope"
                  xmlns:browser="http://namespaces.zope.org/browser"
                  >
         <include package="zc.publication" />

         <adapter
             for="zope.location.interfaces.IRoot
                  zope.publisher.interfaces.browser.IBrowserRequest"
             provides="zope.publisher.interfaces.browser.IBrowserPublisher"
             name="index.html"
             factory="hello.Hello"
             />
       </configure>

    [server:main]
    use = egg:Paste#http
    port = 8080

.. -> src

    >>> open('hello.ini', 'w').write(src)
    >>> app = testapp('hello.ini')

In this example, we didn't specify a root object.  If we don't specify
a root, ``zc.publication`` uses an instance of ``zope.location.Location``
that provides ``zope.location.interfaces.IRoot``.  This allows us to
use views as top-level objects in the URL space.  In this example,
we've registered a view named ``index.html``.  Because ``index.html``
is the default view name, we can access it with either::

   http://localhost:8080/

.. -> url strio

    >>> app.get(url, status=200).body.strip().split() == expected.split()
    True

or::

   http://localhost:8080/index.html

.. -> url strip

    >>> app.get(url, status=200).body.strip().split() == expected.split()
    True


Traversal
=========

In the initial example, we avoided traversal by providing an
application with a single resource and no URL path to traverse.  Most
applications will provide multiple resources.  To provide multiple
resource requires use of the ``zope.publisher`` traversal interfaces.
There are 2 interfaces to be aware of. The first is
``zope.publisher.interfaces.IPublishTraverse``::

    class IPublishTraverse(Interface):

        def publishTraverse(request, name):
            """Lookup a name

            The 'request' argument is the publisher request object.  The
            'name' argument is the name that is to be looked up; it must
            be an ASCII string or Unicode object.

            If a lookup is not possible, raise a NotFound error.
            """

This interface is used to traverse an object with a name.  It's used
when a URL path isn't empty.  The publisher starts with the root
object. If a path isn't empty, it adapts the root object to
``IPublishTraverse`` and calls ``publishTraverse`` on the result of
the adaptation with the first name in the path, which returns a new
object. If there are additional names in the path, the process is
continued with the new object.  When the path is exhausted, the last
object returned by ``publishTraverse`` (or the root object, if the
path is empty) is caled to produce a response.

The second interface to be aware of is
``zope.publisher.interfaces.browser.IBrowserPublisher``::

    class IBrowserPublisher(IPublishTraverse):

        def browserDefault(request):
            """Provide the default object

            The default object is expressed as a (possibly different)
            object and/or additional traversal steps.

            Returns an object and a sequence of names.  If the sequence of
            names is not empty, then a traversal step is made for each name.
            After the publisher gets to the end of the sequence, it will
            call browserDefault on the last traversed object.

            Normal usage is to return self for object and a default
            view name.

            The publisher calls this method at the end of each
            traversal path. If a non-empty sequence of names is
            returned, the publisher will traverse those names and call
            browserDefault again at the end.

            Note that if additional traversal steps are indicated (via a
            nonempty sequence of names), then the publisher will try to adjust
            the base href.
            """

``IBrowserPublisher`` is used for ``GET``, ``HEAD``, and ``POST``
requests to identify a default resource for an object.  Whwn ll of the
steps in a URL path have been traversed, the resulting object is
adapted to this interface and browserDefault is called.  If no names
are returned, then traversal is completed, and the object returned is
published. If names are returned, they are added to the path and
traversal continues from the retirned object. There are 2 use
cases that this interface addresses:

Traversing application objects that are not resources
   If a URL path addresses an application object, you need a way to
   select a resource to display the object.

Controlling how relative URLs are interpreted
   You often want to control how relative URLs are interpreted. For
   example, when a URL addresses a container or an application object,
   you want URLs to be reletive to the object.  Generally, in this
   case, the URL should end with a slash.  If it doesn't, you'll want
   the browser to be redirected to the URL with a slash added, or
   you'll want to set the base href in the page returned.  If a URL
   addresses a resource already, you'll generally want URLs to be
   interpreted relative to the parent URL.

``zc.publication`` registers some default adapters to handle common
cases:

- An adapter for all objects to ``IPublishTraverse`` provides
  traversal by looking up named views.  This allowed traversal from
  the root object to the ``index.html`` view the second example.

- An adapter for all objects to ``IBrowserPublisher`` with an
  ``browserDefault`` method that returns the adapted object and an
  empty path.

- An adapter for ``zope.location.interfaces.ILocation`` to
  ``IBrowserPublisher`` with an ``browserDefault`` method that returns
  the adapted object and a path with the default view name, which it
  arranges to be ``index.html``.

To support more complex traversal models, you'll need to provide these
interfaces yourself, or provide or use other adapters to them.  For
example, if you arrange your content objects in a containment hierarch
using the zope.container framework, you can use the adapters provided
by that framework to provide traversal of the containment hierarchy.

Background
==========

The ``zope.publisher`` framework for creating web applications
requires a publication object that customizes the publisher for a
particular application framework. The ``zope.app.publication`` package (ZAPP)
provides a publication object that provides a framework that provides
capabilities used by most Zope applications, including:

- object traversal from a root object,
- mapping of requests to transactions,
- a security protection system [#protection]_ (using sercurity proxies),
- authentication during traversal to allow multiple authentication domains,
- events to notify applications of key pooints in the request lidecycle,
- error handling with
  - application-provided error views,
  - application-pluggable error logging,
  - request retry to handle conflicting transactions,

ZAPP provides a lot of power and flexibility, but at a
cost.  It can be hard to provide all of the components needed to get
started.

The ZAPP framework was originally used to create a large application
similar to the Zope 2 application.  For lack of a better name, lets
call this application "Z3A".  Z3A included a large number of
components configured with many Zope Configuration Markup (ZCML)
files.  To ease high-level configuration of Z3A, an application
configuration framework based on ZConfig was used to provide a
high-level configuration.  Z3A provided an example of how to build
applications using ZAPP.

While most applications can benefit from most of the features that are
provided by ZAPP, most applications are much simpler than Z3A.  Z3A
provides a poor example of how to create most applications.  It's not
at all clear how to create simpler applications. People often resorted
to copying Z3A and building on it, carrying along components they
didn't need or understand.

Most of the choices made by ZAPP are generally applicable, but 2 are
not [#traveral]_:

- ZAPP assumes the root object for traversal is particular object in
  a ZODB object database.

- ZAPP assumes a security protection scheme based on a particular
  implementation of security proxies.

---------------------------------------------------------------------

.. [#protection] A security protection system is responsible for
   enforcing security restrictions. It is a part of a large security
   architecture that includes authentication, authorization,
   declaration, and protection.

.. [#traversal] It can be argued that traversal isn't a generally
   applicable choice. Certainly, an approach based on URL pattern
   matching is a reasonable approach to traversal, however, traversal
   is a useful approach in many applications, especially application
   with data-driven URL hierarchies.

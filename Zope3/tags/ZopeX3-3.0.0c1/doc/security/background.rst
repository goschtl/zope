An overview of aspects of Zope 3 that are pertinent to its security model
=========================================================================

This document doesn't describe the high-level security model.
Rather, it provides the background for understanding the high-level
security model described in highlevel.rst.

This document should not contain detail about particular services such as
the session service or the authentication service. That's for services.rst.
Nor should this document contain very much about principals, roles,
permissions and so on. That's for highlevel.rst.

Introduction
------------

1. Zope is a server that publishes Python objects to clients over a
   variety of Internet protocols.

1a. "Zope" is available in several different versions. In this document,
   we are concerned only with Zope version 3X.x.x and Zope version 3.x.x.

1b. "Zope 3X" is the preliminary version of Zope 3. It is built from the ground
    up, paying attention to the lessons learned from Zope 2 and CMF. It is not a
    product but intended to let developers get familiar with the new architecture
    early.
    
1c. "Zope 3" is the mainline release intended for production use and including
    backwards compatibility to Zope 2. 

2. Python is an object-oriented language suitable both for writing stand-alone
   scripts and for large-scale software projects. It is implemented in C,
   and comes with a large standard code library. It runs on a number of
   of different operating system platforms, including Solaris, Linux and
   Microsoft Windows.

3. The implementation of Python written in C is properly called cPython.
   There is also an implementation of Python written in Java. Zope works
   only with cPython.

4. A server is one party in the well-known client - server interaction.
   Zope is most often used as a web server, serving HTTP responses to
   web browsers in response to their HTTP requests.
   Zope is also capable of being an FTP server and an XML-RPC server.
   Users can extend Zope to work with other protocols by writing the
   necessary code to do so.

4a. Zope runs in a single process, with multiple threads. So, all software
   calls within zope occur in-process. There's no CORBA or DCOM style
   server sitting around waiting for calls. (XXX rewrite this.)

5. A Python object is a building-block of a software system. An object
   has a set of attributes, identified by name. An attribute represents
   either a piece of data (that is, another object), or a function or
   method that may be 'called' to carry out some instructions.
   Actually, a function is itself a special kind of object. So another
   way of saying the above is that a Python object has a set of attributes,
   identified by name. Some attributes are objects that are useful in
   themselves. Other attributes are 'callable' objects, that are 'called'
   in order to carry out some instructions.

6. Python itself provides no limits on what code may access the attributes
   of an object. Any python code in the same process as a particular object
   may access its attributes if that code has a reference to the object.

7. A class is the template for an object. It provides the means to create
   new objects, provides default values for an object's attributes, and
   provides the callable methods that are available as the attributes of an
   object.

8. Zope provides a facility called "security proxies". An object is enclosed
   in a security proxy, which stands in the way of python code accessing
   the object's attributes. A "checker" guards access to the attributes. This
   is a piece of code that decides whether or not to grant access to the
   requested attribute.
   (add footnote reference to the E language)

9. Traversal, basically a simple 'query' on the components in the Zope system,
   formatted as a URL. Traversal leads to Context. Things can be overridden
   based on context.

Publishing
----------

10. "Publishing" is the process where, upon receiving a request from a client,
   Zope renders a view on an object and returns this to the client.
   For HTTP and FTP, the response takes the form of a sequence of bytes.

10a. To actually publish an object several steps need to be taken. First the
    incoming request needs to be transformed into a standard data structure
    independent of the actual protocol used. Using the information from the
    request we can associate a principal responsible for it and identify the
    requested object using a mechanism called "traversal". 
    Before responding to the request and actually retrieving data from the
    object, the object is wrapped with a security proxy that intermediates
    access to the object using the security management APIs. 

    
    security
    assertions are applied paying respect to the parameters of the principal
    and the object and his context. After retrieving information from the
    object the result needs to be 

    
    form the requests

  convert URL into a sequence of path segments
  traverse from the root to the next object based on the first path segment.
  traversal components

  request
  principal responsible for a request
  response
  request types for different protocols
  error handling

  policy for applying security proxies
  security manager / security context of a request

Component architecture
----------------------

    The component architecture was introduced as a concept to solve a set of
    difficulties that arose during the development of Zope 2. The identified
    goals therefore are: Make explicit declarations of the capabilities and
    intentions an object has. This shall allow easier reuse of code that has
    not necessarily been produced for Zope and simplify deployment of such
    components as well. Reducing the amount of tight dependencies between
    distinct parts of the framework should support a reduced learning curve and
    let people learn the distinct parts bit by bit. 
   

X    A component is an python object with introspectable interfaces. This means
    you can ask an object about the capabilities it has and what it may be used
    for.

X.a

    An interface is a kind of formal contract that describes the fields,
    attributes and methods an object needs to support if it announces ...
    
  explain about interfaces
  1: formal contract of fields, attributes, methods
  2: informal contract in docstrings
  3: type hierarchy of interfaces
  objects implement interfaces
  classes assert that their instances will implement interfaces
  an object can implement interfaces in addition to those its class asserts
  naming convention for interfaces

  adapters
  * provides interfaces for objects that implement a particular interface
  * optional name
  * adapter factories are registered to provide adapters
  * an adapter registry, given an object and a desired kind of adapter, finds
    an appropriate factory to produce that adapter

  views
  * provides a means to present an object to a client
  * a bit like an adapter
  * instead of "object's interface" --> "adapter's interface" we have
    "object's interface", "type of request", "name" --> IPresentation

  services
  * provides a service
  * the fundamentals of the zope system
  * global services that are at the 'process' level, and have no persistent
    state
  * local services that have persistent state
  * services can be overridden, but should defer to higher-up services
  * give a simple example, such as the DB connections service -- root ones
    are available even in lower down places. Although, some are available
    in lower folders that are not available higher up.

  utilities
  * provides a service based on the interface you need to use.
  * don't have the complex overriding+shadowing behaviour of Services.

Transactions and Persistence

  each request in its own transaction
  transaction buzzwords (what parts of ACID do we do?)
  transaction basics: begin(), commit(), abort()
  persistent objects / classes, automatically _p_changed on setting attribute
  database connections, one copy of a persistent object for each connection,
    so no worries about concurrency -- you can write programs as if they
    are single-threaded.

ZODB

  filestorage, python pickles
  other storages
  ZEO


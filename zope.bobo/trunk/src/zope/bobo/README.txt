Bobo 3, Zope 3 for Idiots
=========================

The original Bobo provided Python programmers a very easy way to
create web aplications.  This allowed a lot of people to be productive
quickly and brought many people to Principia, and later Zope.

Zope provides important facilities for complex web applications. Zope
3 provides new and better ways to manage complex applications.
Unfortunately, these techniques may make Zope 3 too heavy for simpler
applications. There's a lot to be learned and remembered.

The later point is particularly interesting.  If a programmer uses
Zope occassionally, it should be easy for them to remember basic ideas
so that they don't have to relearn Zope each time they come back to
it.

Zope is an application server.  One way it supports applications is by
providing folders that can manage content objects. These content
applications can, themselves, be folders. For example, to support a
blog, a wiki, and a bug tracker, one can simply drop blog, wiki, and
tracker objects into a root folder.  To get this however, one must use
the "folder" application and must use the web interface to create the
individual application objects, which must, in turn, live in the ZODB
and follow the rules of persistence.

Some developers want to just write python modules. They don't want to
be forced to use the ZODB or to use the traditional through-the-web
interface of Zope 3. Forcing them to do so violated the "don't make
people do anything" goal of Zope 3.

Zope 3 aspires to be a cloud of components that people can use to
build a variety of applications.  Providing alternative application
models could help to test and refine that mission.

What is *essential* to Zope 3:

- Object publishing, including traversal

- Component Architecture

- Explicit security

- Configuration separate from code

  Does it matter if this is Python? ZCML? ZConfig?

What is *not* essential to Zope 3:

- Persistence or ZODB

- Acquisition

- Folders

- Extensibility

We'll develop a series of examples below that show how to write
applications with Bobo. Each example will introduce a little more
functionality, and a little more complexity.

Hello world
===========

We'll start with the classic simplest application.  We'll write an
application that simply supplied a greeting:

    >>> from zope import bobo

    >>> class Hello(bobo.PublicResource):
    ...
    ...     def __call__(self):
    ...         return 'Hello world!'

Bobo applications are objects that provide some sort of web
interface.  To provide a web interface, objects must implement certain
APIs that support URL traversal and that indicate an explicit intent
to provide the web interfaces. Bobo won't publish objects that don't
provide publishing support.  The `PublicResource` class provides these
APIs.

Bobo also uses the `zope.security` package to protect objects from
unauthorized access.  The `PublicResource` class provides security
declarations that allow us to ignore security issues for applications
that are meant to be public.

Before discussing how to publish the application, we'll use Bobo's
testing server to test our application class. The testing server
simulates the publication process. It lets us try things out without
having to create a network server.

    >>> from zope.bobo.testing import Server
    >>> server = Server(Hello)

    >>> print server.request('GET / HTTP/1.1')
    HTTP/1.1 200 Ok
    Content-Length: 12
    Content-Type: text/plain;charset=utf-8
    <BLANKLINE>
    Hello world!

We initialized the server with our application class.  To test it, we
simply called the `request` method with a request string. Printing the
result displays an HTTP response message.

Note that the output is utf-8 encoded.  Bobo applications should
normally be written using unicode strings.  The publisher
automatically encodes output using the utf-8 text encoding. It also
decodes input using utf-8.

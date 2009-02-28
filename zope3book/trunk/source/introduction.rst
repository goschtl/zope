Introduction
============


Overview
--------

This book is about `Zope 3`_, a Python_ framework for web application
development.  The goal of this book project is to create a complete,
free, open-content, well-organized book for Zope 3.  Zope 3 is
developed by the Zope_ community with the leadership of Jim Fulton,
the creator of original Zope.

Zope 3 consists of a number of small frameworks and libraries written
in Python programming language, and it is usable in whole or in part.
These frameworks and libraries can be put together to build any kind
of web applications.  Most of of the Zope 3 packages are built on top
of a `component architecture`_.  The component architecture helps to
separate presentation code from the problem domain code, and to
create reusable components.

Originally, the term ZOPE was used as an acronym for Z Object
Publishing Environment (the Z doesn't really mean anything in
particular).  However, now-a-days ZOPE is simply written as Zope .

Zope 3 is a ZPL (BSD like, GPL compatible license) licensed free/open
source software.  You can use it for developing commercial and
non-free applications without any licensing fee.

The major components of Zope 3 are:

- object publisher (zope.publisher),
- web server (zope.server)
- transactional object database (ZODB)
- XML based configuration language for registering components
  (zope.configuration)
- flexible security architecture with pluggable security policies
  (zope.security)
- unit and functional testing frameworks (zope.testing,
  zope.testbrowser)
- XHTML-compliant templating language (zope.pagetemplate)
- schema engine and automatic form generation machinery (zope.schema,
  z3c.form)

Apart from the above mentioned packages, there are numerous `packages
available for Zope 3`_.

.. _Zope 3: http://en.wikipedia.org/wiki/Zope_3
.. _Python: http://en.wikipedia.org/wiki/Python_Programming
.. _Zope: http://en.wikipedia.org/wiki/Zope
.. _component architecture:
   http://wiki.zope.org/zope3/ComponentArchitecture
.. _Buildout: http://pypi.python.org/pypi/zc.buildout
.. _packages available for Zope 3:
   http://wiki.zope.org/zope3/Zope3PackageGuide


Scope of the book
-----------------

The intension of this book is not to cover how to use Zope 3 packages
independently or with other Python applications/frameworks.  Rather,
this book focus on developing web applications using Zope 3 packages.
More specifically, this book is not going to cover using Zope 3
technology in Zope 2, Plone, Grok or any other Python
application/framework.  WSGI is also not a current focus of this
book.  This book is not going to cover using `zopeproject` to
bootstrap application (it's very easy, look at the PyPI page for
zopeproject).  This book use Buildout for setting up an isolated
development environment for building applications.  Setuptools and
vitualenv are also covered.


Audience
--------

The target audience of this book are Python programmers looking for
developing web applications.  However, the book doesn't assume you
are familiar with any other web framework.


Prerequisites
-------------

This book will require prior knowledge Python programming language
and at least some exposure to the basics of HTML, CSS and JavaScript.


Brief history
-------------

.. index:: history

The beginning of Zope's story goes something like this, in 1996, Jim
Fulton (CTO of Zope Corporation) was drafted to teach a class on
common gateway interface (CGI) programming, despite not knowing very
much about the subject.  CGI programming is a commonly-used web
development model that allows developers to construct dynamic
websites.  On his way to the class, Jim studied all the existing
documentation on CGI.  On the way back, Jim considered what he didn't
like about traditional, CGI-based programming environments.  From
these initial musings, the core of Zope was written while flying back
from the CGI class.

Zope Corporation (then known as Digital Creations) went on to release
three open-source software packages to support web publishing: Bobo,
Document Template, and BoboPOS.  These packages were written in a
language called Python, and provided a web publishing facility, text
templating, and an object database, respectively.  Digital Creations
developed a commercial application server based on their three
opensource components.  This product was called Principia.  In
November of 1998, investor Hadar Pedhazur convinced Digital Creations
to open source Principia.  These packages evolved into what are now
the core components of Zope 2.

In 2001, the Zope community began working on a component architecture
for Zope, but after several years they ended up with something much
more: Zope 3.  While Zope 2 was powerful and popular, Zope 3 was
designed to bring web application development to the next level.
This book is about this Zope 3, which is not really a new version of
Zope 2.

Most recently, in 2007 the Zope community created yet another
framework based on Zope 3 called Grok.  The original Zope which is
now known as Zope 2 is also widely used.


Organization of the book
------------------------

This book has divided into multiple chapters.  Summary of each
chapter is given below.


Introduction
~~~~~~~~~~~~

Introduce Zope 3 with an overview and scope of the book.  Mention
targetted audience and prerequisites for this book.  Then, briefly go
through the history of Zope 3.  Later, discuss the organization of
the book, and finish with a thanks section.


Getting Started
~~~~~~~~~~~~~~~

This chapter begins with installation details of Python.  Then,
introduce Buildout, the build system used to setup an isolated Python
working environment and its configurations.  Later, it explore
setting up development sandbox using Buildout.  A simple application
is developed further and it ends with creating a `Hello world!` web
page.  During the application development we see how to use ZMI (Zope
Management Interface) briefly.  This chapter also provides a brief
overview of important packages and installation of additional
packages.


Development Tools
~~~~~~~~~~~~~~~~~

This chapter is going to the details of tools required to develop a
web application using Python and Zope components.  You should
familiarize tools like Python eggs, setuptools and buildouts.  If you
are already familiar with these you may skip this chapter.


Interfaces
~~~~~~~~~~

This chapter introduce the concept of interfaces.  If you are already
familiar with this you may skip this chapter.


Component Architecture
~~~~~~~~~~~~~~~~~~~~~~

This chapter introduce Zope component architecture.  If you are
already familiar with this you may skip this chapter.


Testing
~~~~~~~


Setting Up Virtual Hosting
~~~~~~~~~~~~~~~~~~~~~~~~~~


Browser Resources
~~~~~~~~~~~~~~~~~


Browser Pages
~~~~~~~~~~~~~


Content Components
~~~~~~~~~~~~~~~~~~


Skinnig
~~~~~~~


Thanks
------

This book would not be possible if Zope 3 did not exist.  For that,
the I would like to thank all developers of Zope 3.  I am grateful to
Stephan Richter for allowing me to use his book and training material
for this work.

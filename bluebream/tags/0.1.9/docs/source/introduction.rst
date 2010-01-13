.. _intro-intro:

Introduction
============

.. _intro-overview:

Overview
--------

**BlueBream** is a web framework written in Python programming
language.  BlueBream is a free/open source software, owned by
:term:`Zope Foundation`, licensed under Zope Public License (BSD
like, GPL compatible license).  BlueBream was known as **Zope 3** in
the past.  The development of BlueBream, then known as `Zope 3
started in 2001
<https://mail.zope.org/pipermail/zope3-dev/2001-December/000000.html>`_.
BlueBream was developed by the Zope community with the leadership of
Jim Fulton.  A brief history is given in the next section.  There are
many attractive features which make BlueBream unique among Python web
frameworks.

- BlueBream is built on top of :term:`Zope Tool Kit` (ZTK).  In fact,
  ZTK is derived from BlueBream.

- BlueBream use and recommend to use :term:`Buildout` -- a build
  system written in Python.

- BlueBream support WSGI and use Paste (PasteScript & PasteDeploy).

- BlueBream use :term:`Zope Component Architecture` (ZCA) for
  `separation of concerns` and to create highly cohesive reusable
  components (zope.component).

- BlueBream has an object publisher (zope.publisher)

- BlueBream has transactional object database (ZODB)

- BlueBream has an XML based configuration language for registering
  components (ZCML)

- BlueBream has flexible security architecture with pluggable
  security policies (zope.security)

- BlueBream has unit and functional testing frameworks (zope.testing,
  zope.testbrowser),

- BlueBream has XHTML-compliant templating language
  (zope.pagetemplate)

- BlueBream has schema engine and automatic form generation machinery
  (zope.schema, zope.formlib)

The main aim of this book is to create a free on-line book about
BlueBream.  This book will cover how to develop web applications
using BlueBream components. You suggestions and edits are always
welcome.

.. _intro-history:

Brief History
-------------

.. FIXME: we need to improve the history

The beginning of Zope's story goes something like this, in 1996, Jim
Fulton (CTO of Zope Corporation) was drafted to teach a class on
common gateway interface (CGI) programming, despite not knowing very
much about the subject. CGI programming is a commonly-used web
development model that allows developers to construct dynamic
websites. On his way to the class, Jim studied all the existing
documentation on CGI. On the way back, Jim considered what he didn't
like about traditional, CGI-based programming environments. From
these initial musings, the core of Zope was written while flying back
from the CGI class.

Zope Corporation (then known as Digital Creations) went on to release
three open-source software packages to support web publishing: Bobo,
Document Template, and BoboPOS. These packages were written in a
language called Python, and provided a web publishing facility, text
templating, and an object database, respectively. Digital Creations
developed a commercial application server based on their three
open source components. This product was called Principia. In November
of 1998, investor Hadar Pedhazur convinced Digital Creations to open
source Principia. These packages evolved into what are now the core
components of Zope 2.

In 2001, the Zope community began working on a component architecture
for Zope, but after several years they ended up with something much
more: Zope 3 (now renamed to BlueBream). While Zope 2 was powerful
and popular, Zope 3 was designed to bring web application development
to the next level. This book is about this BlueBream (Zope 3), which
is not really a new version of Zope 2.

In 2007 the Zope community created yet another framework based on
Zope 3 called Grok. The original Zope which is now known as Zope 2 is
also widely used.

Very recently Zope 3 project is renamed to BlueBream.

.. _intro-organization:

Organization of the book
------------------------

This book has divided into multiple chapters.  Summary of each
chapter is given below.

Introduction
~~~~~~~~~~~~

This chapter introduce BlueBream with an :ref:`intro-overview` and
:ref:`intro-history`.  Then walks through the
:ref:`intro-organization`.  Finally, ends with :ref:`intro-thanks`
section.

Getting Started
~~~~~~~~~~~~~~~

The :ref:`started-getting` chapter narrate the process of creating a
new web application project using BlueBream.  Also it gives few
exercises to familiarize the basic concepts in BlueBream.

Tutorial
~~~~~~~~

This tutorial chapter explain creating a simple ticket collector
application.  This will help you to familiarize more concepts in
BlueBream.

FAQ
~~~

These are FAQs collected from mailing lists, blogs and other on-line
resources.

HOWTOs
~~~~~~

Small documents focusing on specific topics.

Reference
~~~~~~~~~

A complete reference to BlueBream.

.. _intro-thanks:

Thanks
------

Thanks to all contributors of BlueBream (old Zope 3) for developing
it.  Thanks to all those who contributed to this documentation.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>

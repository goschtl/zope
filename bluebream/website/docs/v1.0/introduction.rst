.. _intro-intro:

Introduction
============

.. _intro-overview:

Overview
--------

:term:`BlueBream` is a web framework written in the Python programming
language.  BlueBream is free/open source software, owned by the
:term:`Zope Foundation`, licensed under the :term:`Zope Public License` (BSD
like, GPL compatible license).  BlueBream was previously known 
as :term:`Zope 3`.

A few of the features which distinguish BlueBream among Python web
frameworks.

- BlueBream is built implements the :term:`Zope Tool Kit` (ZTK), a 
  distillation of many years of experience in meeting demanding 
  requirements for stable, scalable software.

- BlueBream leverages the power of :term:`Buildout` a build
  system written in Python.

- BlueBream supports :term:`WSGI` and uses :term:`Paste` 
  (:term:`PasteScript` & :term:`PasteDeploy`).

- BlueBream features the :term:`Zope Component Architecture` (ZCA) which 
  implements :term:`Separation of concerns` to create highly cohesive reusable
  components (zope.component_).

- BlueBream has an object publisher (zope.publisher_)

- BlueBream has transactional object database (:term:`ZODB`)

- BlueBream offers :term:`ZCML`, an XML based configuration language 
  for registering components, providing limitless flexibility. If you
  don't need the power of ZCML and the complexity it adds, try :term:`Grok`,
  which adds a layer replacing the declarative configuration of ZCML with 
  conventions and declarations in standard Python.

- BlueBream has flexible security architecture with pluggable
  security policies (zope.security_)

- BlueBream has unit and functional testing frameworks (zope.testing_,
  zope.testbrowser_),

- BlueBream has XHTML-compliant templating language
  (zope.pagetemplate_)

- BlueBream has schema engine and automatic form generation machinery
  (zope.schema_, zope.formlib_)

The main aim of this book is to create a free on-line book about
BlueBream.  This book will cover how to develop web applications
using BlueBream components. You suggestions and edits are always
welcome.

.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.publisher: http://pypi.python.org/pypi/zope.publisher
.. _zope.security: http://pypi.python.org/pypi/zope.security
.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _zope.testbrowser: http://pypi.python.org/pypi/zope.testbrowser
.. _zope.pagetemplate: http://pypi.python.org/pypi/zope.pagetemplate
.. _zope.schema: http://pypi.python.org/pypi/zope.schema
.. _zope.formlib: http://pypi.python.org/pypi/zope.formlib

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
~~~~

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


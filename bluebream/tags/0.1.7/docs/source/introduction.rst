Introduction
============

Overview
--------

BlueBream is a web framework written in Python programming language.
BlueBream is a thin layer on top of Zope Tool Kit (ZTK).  Normally,
BlueBream applications are developed using a Python based build
system called Buildout.  BlueBream use the Zope component
architecture (ZCA) for "separation of concerns" and to create
reusable components (zope.component).  BlueBream has an object
publisher (zope.publisher), web server (zope.server), transactional
object database (ZODB), an XML based configuration language for
registering components (ZCML), flexible security architecture with
pluggable security policies (zope.security), unit and functional
testing frameworks (zope.testing, zope.testbrowser), XHTML-compliant
templating language (zope.pagetemplate), schema engine and automatic
form generation machinery (zope.schema, z3c.form) and many other
packages.

Previously BlueBream was known as "Zope 3".  The development of this
project started in 2002.  BlueBream is a ZPL (BSD like, GPL
compatible license) licensed free/open source software.  It was
developed by the Zope community with the leadership of Jim Fulton.  A
brief history is given in the next section.

The main aim of this book is to create a free online book about
BlueBream.  This book will cover how to develop web applications
using BlueBream components. You suggestions and edits are always
welcome.

Brief History
-------------

.. FIXME: we can improve the history

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
opensource components. This product was called Principia. In November
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

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>

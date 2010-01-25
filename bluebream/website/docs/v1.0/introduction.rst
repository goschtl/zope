.. _intro-intro:

Introduction
============

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.

.. _intro-overview:

Overview
++++++++

:term:`BlueBream` is a web framework written in the Python programming
language.  BlueBream is free/open source software, owned by the
:term:`Zope Foundation`, licensed under the :term:`Zope Public License` (BSD
like, GPL compatible license).  BlueBream was previously known 
as :term:`Zope 3`.

A few of the features which distinguish BlueBream among Python web
frameworks.

- BlueBream is built on top of the :term:`Zope Tool Kit` (ZTK), a
  distillation of many years of experience in meeting demanding
  requirements for stable, scalable software.

- BlueBream leverages the power of :term:`Buildout` a build
  system written in Python.
  
- BlueBream uses the :term:`ZODB` transactional object database, providing
  extremely powerful and easy to use persistence.
  
- BlueBream uses :term:`ZCML`, an XML based configuration language 
  for registering components, providing limitless flexibility. If you
  don't need the power of ZCML and the complexity it adds, try :term:`Grok`,
  which adds a layer replacing the declarative configuration of ZCML with 
  conventions and declarations in standard Python.

- BlueBream features the :term:`Zope Component Architecture` (ZCA) which 
  implements :term:`Separation of concerns` to create highly cohesive reusable
  components (zope.component_).

- BlueBream supports :term:`WSGI` using :term:`Paste`, 
  :term:`PasteScript`, and :term:`PasteDeploy`.
  

- BlueBream includes a number of components which provide well tested
  implementation of common requirements. A few are of these are:
  
  - zope.publisher_ publishes Python objects on the web, it is geared
    towards :term:`WSGI` compatibility

  - zope.security_ provides a generic mechanism supporting pluggable 
    security policies

  - zope.testing_ and zope.testbrowser_ offer unit and functional testing 
    frameworks 

  - zope.pagetemplate_ is an XHTML-compliant templating language

  - zope.schema_ and zope.formlib_ provide a schema engine and 
    automatic form generation machinery

.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.publisher: http://pypi.python.org/pypi/zope.publisher
.. _zope.security: http://pypi.python.org/pypi/zope.security
.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _zope.testbrowser: http://pypi.python.org/pypi/zope.testbrowser
.. _zope.pagetemplate: http://pypi.python.org/pypi/zope.pagetemplate
.. _zope.schema: http://pypi.python.org/pypi/zope.schema
.. _zope.formlib: http://pypi.python.org/pypi/zope.formlib

Join our community
++++++++++++++++++

We aim to provide high quality free online documentation for
BlueBream.  If you would like to contribute, the ReStructuredText
source for this website is available from the zope.org repository
(Please replace ``USERNAME`` with your zope.org username.)::

 svn co svn+ssh://USERNAME@svn.zope.org/repos/main/bluebream/website 

If you don't have svn commit access, please follow the `Becoming a
contributor
<http://docs.zope.org/developer/becoming-a-contributor.html>`_
document.  For any queries, please contact us in mailing list or IRC
chat, we can help you to get *reference committer*, which is required
to fill the contributor agreement form.

Stay in touch with BlueBream:

- Mailing List: https://mail.zope.org/mailman/listinfo/bluebream

- Twitter: http://twitter.com/bluebream
   
- Blog: http://bluebream.posterous.com
   
- IRC Channel: `#bluebream at freenode.net <http://webchat.freenode.net/?randomnick=1&channels=bluebream>`_
   
- Google Wave: http://wiki.zope.org/bluebream/BlueBreamWave
   
- PyPI Home : http://pypi.python.org/pypi/bluebream

.. _intro-history:

Brief history
+++++++++++++

.. FIXME: we need to improve the history

Our story begins in 1996, :term:`Jim Fulton` was Technical Director at Digital
Creations. At the IPC (International Python Conference) that year, Jim gave a
presentation on :term:`CGI`: `Python and Internet Programming`_. Jim,
considering CGI less than elegant, envisioned a better way to program for the
internet in Python. According to legend, Jim learned CGI on the plane to the
conference, and designed :term:`Bobo` on the plane ride back home.

Digital Creations then released three open-source Python software packages:
Bobo, Document Template, and BoboPOS.  These packages provided a web publishing
facility, text templating, and an object database and were the core of
*Principia*, a commercial application server.  In November of 1998, investor
Hadar Pedhazur convinced Digital Creations to open source Principia. These
packages evolved into the core components of Zope 2, and Digital Creations
became Zope Corp.

Since those days, Zope has been under active development. It has evolved in
several ways as the community gains experience. We continually seek the optimum
balance between power and ease of use. Zope 2 emphasized rapid development, the
:term:`Zope Component Architecture`.  which is the core of Zope 3 emphasized
modularity and configurability.  This proves very successful in "enterprise"
applications where flexibility and scalability justify the longer learning
curve which Zope 3 required, but is overkill for many situations which
otherwise stand to benefit from the distilled wisdom of the ZCA. The Zope
community has responded to this fact in a number of ways, several projects have
built frameworks which implement :term:`convention over configuration`, and
other refinements of the ZCA components, aimed at facilitating rapid
deployment, with the power of ZCA available under the hood.  Notable among
these are Grok_ and Repoze_.

Zope 3 is now known as BlueBream. The name stems from the fact that the Z
Object Publishing Environment, when spelled `zope`, is the name of a fish.
Another name for the fish is `blue bream`.

BlueBream presents a well defined (and documented) configuration framework
which simplifies managing of the power of the ZCA. We've brought together ZCA,
buildout and Sphinx in a way that makes building powerhouse applications fun.

The components which comprise BlueBream are under continual development by an
international team of extremely experienced coders. Take a look at the recent
uploads to the :term:`PyPi` site, it is rare to not see several ZCA projects
listed.


.. _Python and Internet Programming:
http://www.python.org/workshops/1996-06/agenda.html .. _intro-organization:

Organization of the documentation
+++++++++++++++++++++++++++++++++

This documentation has divided into multiple chapters.  Summary of
each chapter is given below.

Introduction
************

This chapter introduce BlueBream with an :ref:`intro-overview` and
:ref:`intro-history`.  Then walks through the
:ref:`intro-organization`.  Finally, ends with :ref:`intro-thanks`
section.

Getting Started
***************

The :ref:`started-getting` chapter narrate the process of creating a
new web application project using BlueBream.  Also it gives few
exercises to familiarize the basic concepts in BlueBream.

Concepts
********

This chapter discuss important concepts and technologies used in
BlueBream.

Tutorial --- Part 1
*******************

This is the first of the BlueBream tutorial. This chapter walk
through creating a simple ticket collector application.  This will
help you to familiarize more concepts in BlueBream.

Tutorial --- Part 2
*******************

This is the first of the BlueBream tutorial. This chapter continue
the ticket collector application development.  This chapter explain
forms, schemas in more detail.

Manual
******

This is a comprehensive guide to BlueBream.

FAQ
****

These are FAQs collected from mailing lists, blogs and other on-line
resources.

HOWTOs
******

Small documents focusing on specific topics.

Core Development
****************

These documents are written for core development team.  Always visit
the latest documentation site for recent version of these documents
which is actually used by the developers.

Reference
*********

A complete reference to BlueBream.

.. _intro-thanks:

Thanks
++++++

There are many people who contributed to BlueBream through the old
Zope 3 project from 2001.  In fact, many of the technologies came
from Zope 2 project which was started in 1998.  Thanks to all
contributors from 1998 for developing Zope.  It would be difficult to
list all the names here as we don't have enough details.  However a
:ref:`contributors-start` page has created to list names of
new contributors from January 2010.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>


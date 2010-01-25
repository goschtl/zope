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
language.  bluebream is free/open source software, owned by the
:term:`zope foundation`, licensed under the :term:`zope public license` (bsd
like, gpl compatible license).  bluebream was previously known 
as :term:`zope 3`.

a few of the features which distinguish bluebream among python web
frameworks.

- bluebream is built on top of the :term:`zope tool kit` (ztk), a
  distillation of many years of experience in meeting demanding
  requirements for stable, scalable software.

- bluebream leverages the power of :term:`buildout` a build
  system written in python.
  
- bluebream uses the :term:`zodb` transactional object database, providing
  extremely powerful and easy to use persistence.
  
- bluebream uses :term:`zcml`, an xml based configuration language 
  for registering components, providing limitless flexibility. if you
  don't need the power of zcml and the complexity it adds, try :term:`grok`,
  which adds a layer replacing the declarative configuration of zcml with 
  conventions and declarations in standard python.

- bluebream features the :term:`zope component architecture` (zca) which 
  implements :term:`separation of concerns` to create highly cohesive reusable
  components (zope.component_).

- bluebream supports :term:`wsgi` using :term:`paste`, 
  :term:`pastescript`, and :term:`pastedeploy`.
  

- bluebream includes a number of components which provide well tested
  implementation of common requirements. a few are of these are:
  
  - zope.publisher_ publishes python objects on the web, it is geared
    towards :term:`wsgi` compatibility

  - zope.security_ provides a generic mechanism supporting pluggable 
    security policies

  - zope.testing_ and zope.testbrowser_ offer unit and functional testing 
    frameworks 

  - zope.pagetemplate_ is an xhtml-compliant templating language

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

join our community
++++++++++++++++++

we aim to provide high quality free online documentation for
bluebream.  if you would like to contribute, the restructuredtext
source for this website is available from the zope.org repository
(please replace ``username`` with your zope.org username.)::

 svn co svn+ssh://username@svn.zope.org/repos/main/bluebream/website 

if you don't have svn commit access, please follow the `becoming a
contributor
<http://docs.zope.org/developer/becoming-a-contributor.html>`_
document.  for any queries, please contact us in mailing list or irc
chat, we can help you to get *reference committer*, which is required
to fill the contributor agreement form.

stay in touch with bluebream:

- mailing list: https://mail.zope.org/mailman/listinfo/bluebream

- twitter: http://twitter.com/bluebream
   
- blog: http://bluebream.posterous.com
   
- irc channel: `#bluebream at freenode.net <http://webchat.freenode.net/?randomnick=1&channels=bluebream>`_
   
- google wave: http://wiki.zope.org/bluebream/bluebreamwave
   
- pypi home : http://pypi.python.org/pypi/bluebream

.. _intro-history:

brief history
+++++++++++++

.. fixme: we need to improve the history

Our story begins in 1996, :term:`jim fulton` was technical director at digital
creations. At the ipc (international python conference) that year, jim gave a
presentation on :term:`cgi`: `python and Internet programming`_. Jim,
considering cgi less than elegant, envisioned a better way to program for the
internet in python. According to legend, jim learned cgi on the plane to the
conference, and designed :term:`bobo` on the plane ride back home.

Digital creations then released three open-source python software packages:
bobo, document template, and bobopos.  These packages provided a web publishing
facility, text templating, and an object database and were the core of
*principia*, a commercial application server.  In november of 1998, investor
hadar pedhazur convinced digital creations to open source principia. These
packages evolved into the core components of zope 2, and digital creations
became zope corp.

Since those days, Zope has been under active development. It has evolved in
several ways as the community gains experience. We continually seek the optimum
balance between power and ease of use. Zope 2 emphasized rapid development, the
:term:`Zope Component Architecture`.  which is the core of Zope 3, emphasized
modularity and configurability.  This proves very successful in "enterprise"
applications where flexibility and scalability justify the longer learning
curve which Zope 3 requires, but is overkill for many situations which
otherwise stand to benefit from the distilled wisdom of the ZCA. The Zope
community has responded to this in a number of ways, several projects have
built frameworks which implement `convention over configuration`_, and
other refinements of the ZCA components aimed at facilitating rapid
deployment, maintaining the power of ZCA under the hood.  Notable among
these are Grok_ and Repoze_.

Zope 3 is now known as BlueBream. The name stems from the fact that the Z
Object Publishing Environment, when spelled `zope`, is the name of a fish.
another name for the fish is `blue bream`_.

bluebream presents a well defined (and documented) configuration framework
which simplifies managing of the power of the zca. we've brought together zca,
buildout and sphinx in a way that makes building powerhouse applications fun.

The components which comprise BlueBream are under continual development by an
international team of extremely experienced coders. Take a look at the recent
uploads to the `PyPi`_ site, it is rare to not see several zca projects
listed.


.. _convention over configuration: http://en.wikipedia.org/wiki/convention_over_configuration
.. _python and Internet Programming: http://www.python.org/workshops/1996-06/agenda.html 

.. _Grok: http://grok.zope.org/
.. _Repoze: http://repoze.org/
.. _blue bream: http://en.wikipedia.org/wiki/Blue_bream
.. _PyPi: http://pypi.python.org/pypi
.. _intro-organization:

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


.. _intro-intro:

Introduction
============

.. _intro-overview:

Overview
--------

:term:`BlueBream` -- formerly known as :term:`Zope 3` -- is a web framework
written in the Python programming language.

A few features distinguish BlueBream from other Python web frameworks.

- BlueBream is built on top of the :term:`Zope Tool Kit` (ZTK), which has
  many years of experience proving it meets the demanding requirements for
  stable, scalable software.

- BlueBream uses the powerful and familiar :term:`Buildout` system written
  in Python.

- BlueBream employs the Zope Object Database (:term:`ZODB`), a transactional
  object database providing extremely powerful and easy to use persistence.

- BlueBream registers components with Zope Component Markup Language
  (:term:`ZCML`), an XML based configuration language, providing limitless
  flexibility.

- BlueBream features the :term:`Zope Component Architecture` (ZCA) which
  implements :term:`Separation of concerns` to create highly cohesive
  reusable components (zope.component_).

- BlueBream implements Python Web Server Gateway Interface :term:`WSGI`
  using :term:`Paste`, :term:`PasteScript`, and :term:`PasteDeploy`.

- BlueBream includes a number of well tested components to implement common
  activities.  A few are of these are:

  - zope.publisher_ publishes Python objects on the web, emphasizing
    :term:`WSGI` compatibility

  - zope.security_ provides a generic mechanism for pluggable security
    policies

  - zope.testing_ and zope.testbrowser_ offer unit and functional testing
    frameworks

  - zope.pagetemplate_ is an XHTML-compliant language for devloping
    templates

  - zope.schema_ is a schema engine

  - zope.formlib_ is a tool for automatically generating forms

BlueBream is free/open source software, owned by the :term:`Zope
Foundation`.  Bluebream is licensed under the :term:`Zope Public License`
(BSD like, GPL compatible license).

.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.publisher: http://pypi.python.org/pypi/zope.publisher
.. _zope.security: http://pypi.python.org/pypi/zope.security
.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _zope.testbrowser: http://pypi.python.org/pypi/zope.testbrowser
.. _zope.pagetemplate: http://pypi.python.org/pypi/zope.pagetemplate
.. _zope.schema: http://pypi.python.org/pypi/zope.schema
.. _zope.formlib: http://pypi.python.org/pypi/zope.formlib

.. _intro-join-community:

Join our community
------------------

**We invite you to become part of our community!**

You can become part of our community by joining/subscribing to these
community platforms:

- Mailing list: https://mail.zope.org/mailman/listinfo/bluebream

- Twitter: http://twitter.com/bluebream

- Blog: http://bluebream.posterous.com

- IRC channel: `#bluebream at freenode.net
  <http://webchat.freenode.net/?randomnick=1&channels=bluebream>`_

- Wiki: http://wiki.zope.org/bluebream

- Ohloh.net: https://www.ohloh.net/p/bluebream

- PyPI Page: http://pypi.python.org/pypi/bluebream

The BlueBream developer community is an active community involved in the
development of BlueBream itself and is looking for contributors.
Development related information is documented in the `wiki
<http://wiki.zope.org/bluebream/ContributingToBlueBream>`_.

We aim to provide high quality, free online documentation for BlueBream.  If
you would like to contribute, the `RestructuredText
<http://docutils.sourceforge.net/rst.html>`_ source for this website is
available from the zope.org repository (please replace ``USERNAME`` with
your zope.org username.)::

 svn co svn+ssh://USERNAME@svn.zope.org/repos/main/bluebream/website

If you don't have svn commit access, please consult: `becoming a contributor
<http://docs.zope.org/developer/becoming-a-contributor.html>`_ document.  If
you have any questions, please contact us in mailing list or irc chat.  We
are happy to assist you with submitting the contributor agreement form
required to become a *committer*.

.. _intro-history:

Brief history
-------------

.. FIXME: we need to improve the history

Our story begins in 1996.  :term:`Jim Fulton` was technical director at
digital creations.  At the International Python Conference (IPC) that year,
Jim gave a presentation on :term:`CGI`: `Python and Internet Programming`_.
Jim, considering CGI less than elegant, envisioned a better way to program
for the internet in Python.  According to legend, Jim learned CGI on the
plane to the conference, and designed :term:`Bobo` on the plane ride back
home.

Digital Creations then released three open-source Python software packages:
Bobo, Document Template, and Bobopos.  These packages -- a web publisher, a
text template, and an object database -- were the core of *Principia*, a
commercial application server.  In November of 1998, investor Hadar Pedhazur
convinced Digital Creations to open source Principia.  These packages
evolved into the core components of Zope 2 and Digital Creations became Zope
Corporation.

Since those days Zope has been under active development.  It has evolved in
several ways as the community gained experience, continually seeking the
optimum balance between power and ease of use.  Zope 2 emphasized rapid
development, the :term:`Zope Component Architecture`, which is the core of
Zope 3, emphasized modularity and configurability which proved very
successful in "enterprise" applications requiring flexibility and
scalability.

Zope 3 is now known as BlueBream.  The name stems from the coincidence that
the Z Object Publishing Environment when spelled `zope` is the name of a
species of fish.  `Blue bream`_ is another name for the same species.

BlueBream combines the ZCA, Buildout into a well defined, and documented,
that makes building powerhouse applications fun.

The components which comprise BlueBream are under continual development by
an international team of experienced coders.

The longer learning curve for deploying Zope 3 is overkill for some
situations which would otherwise stand to benefit from the distilled wisdom
of the ZCA.  The Zope community has responded to this in with several
rapidly deployable ZCA-derived frameworks, which implement Convention over
configuration while maintaining the power of ZCA under the hood.  Notable
among these are :term:`Grok`: and Repoze.  Take a look at the recent uploads
to the PyPI site, it is rare to not see several ZCA projects listed.

.. _Convention over configuration: http://en.wikipedia.org/wiki/Convention_over_configuration

.. _python and Internet Programming: http://www.python.org/workshops/1996-06/agenda.html

.. _Repoze: http://repoze.org/
.. _Blue bream: http://en.wikipedia.org/wiki/Blue_bream
.. _PyPi: http://pypi.python.org/pypi
.. _intro-organization:

.. _intro-more-about-project:

More about the project
----------------------

The original intent of Zope 3 was to become a replacement for Zope 2,
however this did not happen as planned.  Instead Zope 2 continued to make up
the majority of new Zope deployments, mostly due to the popularity of Plone.

Zope 3 was conceived as a fresh start to leave certain aspects and
limitations of its presumed predecessor `Zope 2
<http://docs.zope.org/zope2/zope2book/>`_ behind.  Zope 3 introduced a new
component architecture to address some of the inheritance-based-programming
limitations of Zope 2.

The `ZCA <http://www.muthukadan.net/docs/zca.html>`_ notionally includes the
packages named ``zope.component``, ``zope.interface`` and
``zope.configuration``.  Zope 3 added to this a large number of extra
libraries and provided an application server that enabled programmers to
develop standalone web applications.

In the meantime another wave of web frameworks appeared.  :term:`Grok`
evolved with many Zope 3 libraries at its core.  `repoze.bfg (aka BFG)
<http://bfg.repoze.org>`_ evolved around the ZCA.  Additionally Zope 2 began
to make use of the ZCA and various other Zope 3 packages.

In 2009 a group of Zope developers agreed to concentrate primarily on the
development of the Zope 3 libraries and formed the Zope Toolkit (ZTK) that
focused on a slim library subset of the Zope 3 project, which can then be
efficiently utilized by web application frameworks on top.  This development
led to the following logical steps:

- Form a project around the remaining web application part of Zope 3

- Name it BlueBream as a new and unique name to avoid confusion

- Create an upgrade path from the former Zope 3 application server

BlueBream can thus be seen as the successor of Zope 3 web application server
that like Grok relies on the ZTK.

.. _intro-organization-doc:

Organization of the documentation
---------------------------------

This documentation has divided into multiple parts and chapters.  A summary
of each parts and chapters is given below.

Getting Started
~~~~~~~~~~~~~~~

The :ref:`started-getting` chapter narrate the process of creating a new web
application project using BlueBream.  It also gives a few exercises to
demonstrate the basic concepts of BlueBream.

Concepts
~~~~~~~~

The :ref:`concepts` chapter provides an overview of important concepts and
technologies used in BlueBream.  It recommended to re-visit this chapter
after finishing tutorials.

Tutorial --- Part 1
~~~~~~~~~~~~~~~~~~~

This :ref:`chapter <tut1-tutorial>` presents a tutorial exercise
demonstrating how to build a simple ticket collector application using
BlueBream.  Part 1 introduces basic BlueBream concepts.

Tutorial --- Part 2
~~~~~~~~~~~~~~~~~~~

This :ref:`chapter <tut2-tutorial>` is a continuation of the ticket
collector application tutorial excercises, providing more detail regarding
forms and schemas.

Tutorial --- Part 3
~~~~~~~~~~~~~~~~~~~

This :ref:`chapter <tut3-tutorial>` is a continuation of the ticket
collector application tutorial.  This chapter cover skinning with BlueBream.

Tutorial --- Part 4
~~~~~~~~~~~~~~~~~~~

This :ref:`chapter <tut4-tutorial>` is a continuation of the ticket
collector application tutorial.  This chapter cover Security related things
like users, roles & permissions.

Manual
~~~~~~

This part contains a comprehensive manual to BlueBream.  Manual is divided
into various chapters which cover different topics in BlueBream.

FAQ
~~~

This is the :ref:`Frequently Asked Questions <faq-faq>` (FAQs) with answers!
collected from mailing lists, blogs and other on-line resources.

HOWTOs
~~~~~~

These :ref:`HOWTO documents <howto>` contains brief explanations of special
topics with step-by-step solutions.

Core Development
~~~~~~~~~~~~~~~~

This :ref:`part <core-development>` contains explanations written for the
core development team.  Developers should always consult the latest
documentation site for changes to the documentation in this section.

Reference
~~~~~~~~~

This :ref:`part <reference>` provides a complete reference to BlueBream
packages and important features.  This part also has reference documentation
for ZCML, standard events & common errors.

Documentation for Community Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This :ref:`part <community-docs>` cover documentation for various community
packages.


.. _intro-thanks:

Thanks
------

BlueBream truly stands on the shoulders of giants.  Zope 3 was built on the
concepts of Zope 2 which was built on Bobo and friends.  The list of Zope
Corporation alumni is a *Who's Who* of Python development, including one
*Guido Van Rossum*.  For more than 10 years contributions have come from a
world-wide community.  We thank you all.  Please help us add more names to
the list of contributor as we move forward from January 2010.

:ref:`List of contributors <contributors-start>`

.. _intro-translations:

Translations
------------

- `Russian <http://bit.ly/92jl9Q>`_

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the discussion
  thread.</a></noscript><a href="http://disqus.com" class="dsq-brlink">blog
  comments powered by <span class="logo-disqus">Disqus</span></a>

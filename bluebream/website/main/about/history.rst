.. _history:

The history of BlueBream
========================

Our story begins in 1996.  `Jim Fulton` was technical director at digital
creations.  At the International Python Conference (IPC) that year, Jim gave
a presentation on `CGI`: `Python and Internet Programming`_.  Jim,
considering CGI less than elegant, envisioned a better way to program for
the internet in Python.  According to legend, Jim learned CGI on the plane
to the conference, and designed `Bobo` on the plane ride back home.

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
development, the `Zope Component Architecture`, which is the core of Zope 3,
emphasized modularity and configurability which proved very successful in
"enterprise" applications requiring flexibility and scalability.

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
among these are Grok and Repoze.  Take a look at the recent uploads to the
PyPi site, it is rare to not see several zca projects listed.

.. _Convention over configuration: http://en.wikipedia.org/wiki/Convention_over_configuration

.. _python and Internet Programming: http://www.python.org/workshops/1996-06/agenda.html

.. _Repoze: http://repoze.org/
.. _Blue bream: http://en.wikipedia.org/wiki/Blue_bream
.. _PyPi: http://pypi.python.org/pypi
.. _intro-organization:

.. _intro-more-about-project:


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

In the meantime another wave of web frameworks appeared.  `Grok` evolved
with many Zope 3 libraries at its core.  `repoze.bfg (aka BFG)
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

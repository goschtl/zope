Summary of concepts
-------------------

We summarize some terms and concepts so we can all agree on how we
refer to things in discussions.

Zope 2
    the Zope 2 application server.

Zope 3 (preferred: Zope 3 application server)
  Zope 3 as an application server, includes a way to create projects.
  Currently also contains the ZMI. Since 2010, Zope 3 as an application server
  has been renamed to BlueBream.

BlueBream
    BlueBream is the new name of Zope 3 as an application server. It consists in
    a project template and it uses the Zope Toolkit. It also provides a
    migration path from Zope 3.4.

Grok web framework
    Grok, very similar to BlueBream, but with extra Grok libraries and policy,
    and Grok community.

Repoze
    a set of libraries that builds on Zope technology, reuse Zope concepts and
    expand on Zope technology.

Plone
    a CMS based on Zope 2 and the CMF.

CMF
    The Content Management Framework for Zope 2, on which are based applications
    such as Plone or CPS.

Zope Toolkit
    the collection of Zope Toolkit core libraries. Shouldn't include the ZMI
    and doesn't include a particular way to create a project.

Zope Toolkit release
    a set of Zope Toolkit library versions that have been tested to work
    together. This set receives a collective version number ("Zope Toolkit
    3.5"). A release could simply consist of a list of version numbers.

Zope Toolkit Steering Group
    the group responsible for the leading Zope Toolkit development, ensuring
    its continued evolution driven by the concerns of the various consumers of
    the toolkit (or particular libraries in the toolkit).

Zope core library
    a library within the Zope Toolkit.

Zope extra library
    a library not within the Zope Toolkit. Could be "just not" within the Zope
    Toolkit, or "not yet", or "not anymore". These libraries are intended to
    work with the Zope Toolkit and are maintained by the wider Zope community.

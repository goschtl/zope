Creating Local Site Manager
===========================

Quick start
-----------

This document explains creating of a local site manager.  Local site
manager provides a persistent component registry where local
components like local utilities can be registered.  To try the
examples given here, you can create a project as explained in the
:ref:`started-getting` document.  Here is the commands to create a
sample project.::

  $ easy_install bluebream
  $ paster create -t bluebream sampleproject python_package=mycompany.main
  $ cd sampleproject

  $ python bootstrap.py
  $ ./bin/buildout

To add a local site manager to the sample application, you need to
add one line of code to ``AddSampleApplication`` class in
``src/mycompany/main/welcome/views.py`` file, inside ``createAndAdd``
method just before the last line::

  app.setSiteManager(LocalSiteManager(app))

Be sure to add the following import to the top of the file::

  from zope.site import LocalSiteManager

So, the last three lines will look like this::

  self.context[name] = app
  app.setSiteManager(LocalSiteManager(app))
  self.request.response.redirect(name)

That's it. Now, each added using this form will be a "site". But what
does it mean?

Site Managers
-------------

*Site* is persistent object used to provide custom component setups
for a part of your application or whole web site. For this, it
contains *Site Manager*, which is:

1. container for local components
2. and it has local registry for those components.

Imagine hierarhy in ZODB::

  root---------FIRST
  |
  +---(++etc++site)---RootCookieManager
  |
  +-----------------app-------------SECOND
                      |
                      +---(++etc++site)---AppCookieManager

``++etc++site`` means `Local Site Manager` itself. Thus, ``root`` and
``app`` are *Sites*.  Let's make ``RootCookieManager`` and
``AppCookieManager`` to be utilities registered in their `Site
Managers` as utilities provide interface
``zope.session.interfaces.IClientIdManager`` and with empty name.

Let's query unnamed utility provided interface
``zope.session.interfaces.IClientIdManager``:

- if you search the utility using context ``root`` then you will get ``RootCookieManager``.
- ... using context ``FIRST`` then you will get ``RootCookieManager``.
- ... using context ``app`` then you will get ``AppCookieManager``.
- ... using context ``SECOND`` then you will get ``AppCookieManager``.

It was local site managers and local (persistent) components.  There
are yet another sort of registry - global component registry (global
site manager), which you have use for registering non-persistent
components.  We will not explain it in this document.

How does it usually look like ?
-------------------------------

When do you need local utilities? Here are reasons to create local
utility:

- you need persistent object and you need to edit its attributes or
  it should contain other objects

- you require this object in a single copy (i.e. `singleton
  <http://en.wikipedia.org/wiki/Singleton_pattern>`_)

- you need to have the ability to fetch this object from everywhere
  in your site (see example with nested objects in previous section)

Which local utilities are commonly used? List of interfaces they
provide:

- ``zope.intid.interfaces.IIntIds`` this utility assigns unique ids
  to objects.

- ``zope.catalog.interfaces.ICatalog`` contains and manage search
  indexes.

- ``zope.authentication.interfaces.IAuthentication`` provide support
  to establish principals for requests.

Use event handler
-----------------

In the add form above you set Site Manager directly in the form.  But
let's separate this logic from view.  Events system is another edge
of polyhedron of component architecture used in BlueBream.  Event
caller and event handler do not know about each other and even do not
require each other.

Event caller
  We needn't write caller for this event, because it is done by
  container itself.  When you add object into container, it calls
  event which provides interface
  ``zope.lifecycleevent.interfaces.IObjectAddedEvent``.

Event handlers
  Handlers in BlueBream (generally, in ZTK) are subscription adapter
  factories that don't produce anything.  This implies a lot of
  interesting possibilities, but will not consider them in this
  document.  Just write it - it is simple function (`handler.py`)::

    from zope.site import LocalSiteManager

    def siteAdded(site, event):
        site.setSiteManager(LocalSiteManager(site, False))
        sm = site.getSiteManager()

  and register this function as handler for events which provide
  interface ``IObjectAddedEvent`` (`configure.zcml`)::

    <subscriber
        for="sample.welcome.interfaces.ISampleApplication
             zope.app.container.interfaces.IObjectAddedEvent"
        handler=".handler.siteAdded"
        />

ISite interface
---------------

We showed above: "*Site* is a persistent object used..." But in
terminology of component architecture we do not need to speak about
objects, i.e. about implementations.  It is enough to speak about
interfaces which these objects do provide.

In this "language" *Site* is object which provides interface
``zope.component.interfaces.ISite``.  And it happens automatically
after we set Local Site Manager.  But to do this, we need object
which implements ``zope.component.interfaces.IPossibleSite``.  That
is why you have used ``zope.site.folder.Folder`` container.  Thus,
there are convertation::

  IPossibleSite ---> ISite

Summary
-------

1. There are local component registry and global component registry.

2. Accordingly, local components and global components are registered
   in these registries.

3. Local component registry named usually `Local Site Manager`
   (technically, it contains the registry).

4. It contained in object which provide
   ``zope.component.interfaces.ISite`` interface.

5. To make this, you need to use object, which provide interface
   ``zope.component.interfaces.IPossibleSite``, and call its method
   ``setSiteManager``.

6. Good place to do this - `Event Handler` which is subscribed to 2
   interfaces: your custom site's interface and
   ``zope.lifecycleevent.interfaces.IObjectAddedEvent``.

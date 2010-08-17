.. _tut3-tutorial:

Tutorial --- Part 3
===================

.. _tut3-intro:

Introduction
------------

It is often required to build web applications with equal/similar features,
but different look and feel.  Variation of look and feel can be simple or
complex.  It can be either just an exchange of a CSS file and some images.
Sometimes, you will be required to reconfigure the application to have
different user interface components, such as widgets, tables etc.  Also you
will be required to mix and match user interface components from multiple
packages.

There are two terms associated with skinning named, `layer` and `skin`.
Before proceeding, it would be better to understand the meaning of these two
terms in BlueBream skinning.

Layers
~~~~~~

A layer define the **feel** of an application user interface.  Layer
contains the presentation logic of the application.  Presentation logic
involves the layout of pages and placement of widgets.  Some common
artifacts of layer are pages, content providers, viewlet managers and
viewlets.  Layers are normally developed by BlueBream (Python) developers.

Skins
~~~~~

A skin define the **look** of a an application user interface. Common
artifacts of skins are templates (ZPT) and resources (CSS, Javascript,
etc.).  Skin use layers to retrieve the data for templates.  Skins are
normally developed by HTML and graphic designers.

Layers versus skins
~~~~~~~~~~~~~~~~~~~

Both layers and skins are implemented as interfaces.  Technically speaking,
BlueBream does not differentiate between layers and skins.  In fact, the
distinction of layers defining the **feel** and skins the **look** is a
convention.  You may not want to follow the convention, if it is too
abstract for you, but if you are developing application with multiple look
and feel, it is strongly suggested using this convention, since it cleanly
separates concerns.

Both layers and skins support inheritance/acquisition.  This is realized
through a combination of interface inheritance and component lookup
techniques.

There are some skins available with BlueBream.  Unfortunately, it is hard to
reuse the UI components developed for these skins, since they still rely on
the not so flexible macro pattern.  Thus, it is better if you start from
scratch.  This will also avoid a lot of the overhead that comes with the
over-generalized core skins.  In future, those core skins will be removed or
replaced.

This chapter discuss creating a new skin for ticket collector application.
It is reccomented to use a skin created from scratch to develop BlueBream
applications.

A new skin
----------

All views are registered for ``default`` layer by default.  So, you need not
to explicitly mention the layer to get registered for ``default`` layer.
The interface which define the default layer is located here:
``zope.publisher.interfaces.browser.IDefaultBrowserLayer``.  The default
layer contains a lot of things you do not need (security concerns).  Since
pretty much everything in ``zope.app`` is registered into the default layer,
it has an uncontrollable amount of junk in it.  It is very hard to verify
that all those registrations fulfill your security needs.  Another problem
is that views might be available that you do not want to be available.  It
is reccommended to develop skins from scratch.  But some registrations in
the default layer are very useful.  Examples of those useful registrations
include error views, traversal registrations, and widgets.


Setting up a layer
------------------

You can create a new package named *skin* inside *tc* namespace.  All the
skin related things will be added here.  First create the ``skin`` directory
and ``__init__.py`` file to make it a Python package::

  $ mkdir src/tc/skin
  $ echo "#Python Package" > src/tc/skin/__init__.py

The skin definition will be placed in ``src/tc/skin/interfaces.py`` and the
registration in ``src/tc/skin/configure.zcml``.  To create a new layer, you
need to write an interface of the type ``IBrowserSkinType``.  You can create
``ITCLayer`` as given below in ``src/tc/skin/interfaces.py``::

  from zope.publisher.interfaces.browser import IBrowserSkinType

  class ITCLayer(IBrowserSkinType):
      """Ticket collector application layer"""


.. note:: **Interface type**

  The ``IBrowserSkinType`` is an interface type similar to ``Interface``.
  To create an interface type, you can create an interface inheritting from
  ``zope.interface.interfaces.IInterface``.  For example::

    from zope.interface.interfaces import IInterface

    class IMyInterfaceType(IInterface):
        """My interface type"""

To use this layer, you can change all page, viewletmanager, and viewlet
directives to specify this layer::

  layer="tc.skin.interfaces.ITCLayer"


Setting up a skin
-----------------

Skins are also interfaces defined using ``zope.interface`` package.  You can
created skin interfaces by inheritting from the layer interface.  For
example, here is the ``ITCSkin`` inheritted from ticket collector
application layer (``ITCLayer``)::

  class ITCSkin(ITCLayer):
      """Skin for ticket collector app."""

To register this you can use ``interface`` and ``utility`` directives in
``zope`` namespace.  Add this to ``src/tc/skin/configure.zcml``::

  <configure
     xmlns="http://namespaces.zope.org/zope"
     xmlns:browser="http://namespaces.zope.org/browser"
     i18n_domain="ticketcollector">

    <interface
        interface="tc.skin.interfaces.ITCSkin"
        type="zope.publisher.interfaces.browser.IBrowserSkinType"
        />

    <utility
        component="tc.skin.interfaces.ITCSkin"
        provides="zope.publisher.interfaces.browser.IBrowserSkinType"
        name="TCSkin"
        />

  </configure>

As a shortcut, you can also just use the ``interface`` directive and
pass the ``name`` parameter.  The following one directive has the
same effect as the two above regarding the skin registration::

  <interface
      interface="tc.skin.interfaces.ITCSkin"
      type="zope.publisher.interfaces.browser.IBrowserSkinType"
      name="TCSkin"
      />

The skin definition is complete now, but it is not yet included from the
main package.  To include this package in the main package (``tc.main``) you
need to modify the ``src/tc/main/configure.zcml`` and add this line before
``</configure>``::

  <include package="tc.skin" />

You can register all templates for this skin by adding the layer attribute::

  layer="tc.skin.interfaces.ITCSkin"

As you can see, you don't have to create an extra layer just to create a
custom skin.  But it is not reccommended to declare any views for the skin
directly, rather you can register for the layer.

Updating various views
----------------------

Update the ``add_ticket_collector`` view in
``src/tc/collector/configure.zcml`` with ::

  <browser:page
     for="zope.site.interfaces.IRootFolder"
     name="add_ticket_collector"
     permission="zope.Public"
     class="tc.collector.views.AddTicketCollector"
     layer="tc.skin.interfaces.ITCSkin"
     />

Also update the default ``index`` page for ``ICollector`` with new layer in
``src/tc/collector/configure.zcml``::

  <browser:page
     for="tc.collector.interfaces.ICollector"
     name="index"
     permission="zope.Public"
     class="tc.collector.views.TicketCollectorMainView"
     layer="tc.skin.interfaces.ITCSkin"
     />

You can do the same thing for all other views::

  <browser:page
     for="tc.collector.interfaces.ICollector"
     name="add_ticket"
     permission="zope.Public"
     class="tc.collector.views.AddTicket"
     layer="tc.skin.interfaces.ITCSkin"
     />

  <browser:page
     for="tc.collector.interfaces.ITicket"
     name="index"
     permission="zope.Public"
     class="tc.collector.views.TicketMainView"
     layer="tc.skin.interfaces.ITCSkin"
     />

  <browser:page
     for="tc.collector.interfaces.ITicket"
     name="add_comment"
     permission="zope.Public"
     class="tc.collector.views.AddComment"
     layer="tc.skin.interfaces.ITCSkin"
     />

Using the skin
--------------

To access a skin, you need to use ``++skin++`` in the begining of the path
followed by the skin name.  For example, if the skin name is ``TCSkin``, the
site can be accessed like this: ``http://localhost:8080/++skin++TCSkin``

You can hide the skin traversal step by using Apache's virtual
hosting feature.

To change the default skin to something else use the ``browser:defaultSkin``
directive.  You can set ``TCSkin`` as the default skin like this::

  <browser:defaultSkin name="TCSkin" />

You can add this declaration in the ``etc/overrides.zcml`` file.  So that it
will be overridden by the previous declaration, if there is any.

Using CSS resource files
------------------------

.. note:: This section should explain using browser resources to work with
   CSS files.  For more details refer: :ref:`man-browser-resource`

Summary
-------

This chapter introduced concepts related to BlueBream skinning.  This
chapter also explained howto create layers and skins from scratch.

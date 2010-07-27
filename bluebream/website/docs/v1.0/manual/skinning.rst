.. _man-browser-skinning:

Skinning
========

Introduction
------------

It is often required to build web applications with equal/similar
features, but different look and feel.  Variation of look and feel
can be simple or complex.  It can be either just an exchange of a CSS
file and some images.  Sometimes, you will be required to reconfigure
the application to have different user interface components, such as
widgets, tables etc.  Also you will be required to mix and match user
interface components from multiple packages.

In BlueBream, the skin concept is implemented to use the Zope
component architecture.

There are two terms associated with skinning named, `layer` and
`skin`.  Before proceeding, it would be better to understand the
meaning of these two terms in BlueBream skinning.  Skins are directly
provided by a request

Layers
~~~~~~

* Define the "feel" of a site

* Contain presentation logic

* Common artifacts: pages, content providers, viewlet managers, and
  viewlets

* Developed by BlueBream (Python) developers


Skins
~~~~~

* Define the "look" of a site

* Common artifacts: templates and resources (CSS, Javascript, etc.)

* Use layers to retrieve the data for templates

* Developed by HTML and Graphic Designer/Scripter


Layers versus skins
~~~~~~~~~~~~~~~~~~~

* Both are implemented as interfaces

* BlueBream does not differentiate between the two

* In fact, the distinction of layers defining the "feel" and skins
  the "look" is a convention. You may not want to follow the
  convention, if it is too abstract for you, but if you are
  developing application with multiple look and feel, it is strongly
  suggested using this convention, since it cleanly separates
  concerns.

* Both support inheritance/acquisition

This is realized through a combination of interface inheritance and
component lookup techniques.  This book will discuss this in more
detail later.

Unfortunately, it is hard to reuse the UI components developed for
these skins, since they still rely on the not so flexible macro
pattern.  Thus, it is better if you start from scratch.  This will
also avoid a lot of the overhead that comes with the over-generalized
core skins.

A new skin
----------

* Views registered for default layer by default
  ``zope.publisher.interfaces.browser.IDefaultBrowserLayer``

* Default layer contains a lot of things you do not need (security
  concerns)

* Since pretty much everything in ``zope.app`` is registered into the
  default layer, it has an uncontrollable amount of junk in it.  It
  is very hard to verify that all those registrations fulfill your
  security needs.  Another problem is that views might be available
  that you do not want to be available.

* Always want to develop skins from scratch

* Some registrations in the default layer are very useful

* Examples of those useful registrations include error views,
  traversal registrations, and widgets.


Setting up a layer
~~~~~~~~~~~~~~~~~~

Write an interface for the layer that inherits the minimal layer::

  from zope.publisher.interfaces.browser import IBrowserSkinType

  class IHelloWorldLayer(IBrowserSkinType):
      """Hello World Application Layer"""


Change all page, viewletmanager, and viewlet directives to specify
this layer::

  layer=".interfaces.IHelloWorldLayer"

Once you changed those registrations, the `helloworld.html` page will
not be available anymore in the core skins.  The templates by themselves
do not matter.


Using layer
~~~~~~~~~~~

Registering views and resources is not any different now, but you can
simply register them on the skin directly::

  <browser:resource
      name="zope3logo.gif" 
      file="images/zope3logo.gif" 
      layer=".interfaces.IBasicSkin"
      />

As you can see, you don't have to create an extra layer just to
create a custom skin.  You were also able to use standard Component
Architecture ZCML directives instead of custom ones whose special
syntax the developer needs to remember additionally.

A typical ``browser:page`` with with layer specified is like this::

  <browser:page
      for="*"
      name="dialog_macros"
      permission="zope.View"
      layer=".interfaces.IBasicSkin"
      template="dialog_macros.pt"
      />


Setting up a skin
~~~~~~~~~~~~~~~~~

Skins are technically interfaces defined using ``zope.interface``
package.  Write an interface for each new skin that inherits the Hello
World application layer::

  class IBasicSkin(IHelloWorldLayer):
      """Basic Skin for Hello World App."""

To register this you can use ``interface`` and ``utility`` directives
in ``zope`` namespace.  The type of the ``IShanghaiSkin`` skin is
``zope.publisher.interfaces.browser.IBrowserSkinType``.  Here is a
sample ``configure.zcml``::

  <interface
      interface=".interfaces.IBasicSkin"
      type="zope.publisher.interfaces.browser.IBrowserSkinType"
      />

  <utility
      component=".interfaces.IBasicSkin"
      provides="zope.publisher.interfaces.browser.IBrowserSkinType"
      name="BasicSkin"
      />

As a shortcut, you can also just use the ``interface`` directive and
pass the ``name`` parameter.  The following one directive has the
same effect as the two above regarding the skin registration::

  <interface
      interface=".interfaces.IBasicSkin"
      type="zope.publisher.interfaces.browser.IBrowserSkinType"
      name="BasicSkin"
      />

Register all templates for this skin by adding the layer attribute::

  layer=".interfaces.IBasicSkin"


Using the skin
~~~~~~~~~~~~~~

To access a skin, you need to use ``++skin++`` in the begining of the
path followed by the skin name.  For example, if the skin name is
``BasicSkin``, the site can be accessed like this:
``http://localhost:8080/++skin++BasicSkin``

You can hide the skin traversal step by using Apache's virtual
hosting feature.

To change the default skin to something else use the
``browser:defaultSkin`` directive.  You can set ``BasicSkin`` as the
default skin like this::

  <browser:defaultSkin name="BasicSkin" />

You can add this declaration in the ZCML file where you are defining
the skin & layer interfaces.

Summary
-------

This chapter introduced skinnig in BlueBream.

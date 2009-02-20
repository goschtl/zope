Skinnig
=======

Motivation

* Need to build sites with equal/similar features, but different look
  and feel

* Variation of Look and Feel can be simple or complex

  - Exchange a CSS file and some images

  - Reconfigure the application to have different UI components, such
    as widgets, tables, O-wrap, etc.

* Often need to mix and match UI components from multiple packages

The level of customization of Zope (2 and 3) has been a strong point
for years. Initially the UI was customized relying on implicit
acquisition, where it was simply a matter of adding an object higher
in the object path to customize the UI. Since implicit acquisition is
often hard to debug, the CMF introduced the concept of skins, where a
skin describes the look and feel of a site. Skins could acquire from
other skins explicitly.

In Zope 3 the concept of skins was reconsidered and re-implemented to
use the component architecture.

Layers

* Define the "feel" of a site

* Contain presentation logic

* Common artifacts: pages, content providers, viewlet managers, and
  viewlets

* Developed by Zope 3 Python developers

Skins

* Define the "look" of a site

* Common artifacts: templates and resources (CSS, Javascript, etc.)

* Use layers to retrieve the data for templates

* Developed by HTML and Graphic Designer/Scripter

Layers versus Skins

* Both are implemented as interfaces

* Zope 3 does not differentiate between the two

* In fact, the distinction of layers defining the "feel" and skins
  the "look" is a convention. You may not want to follow the
  convention, if it is too abstract for you, but if you are
  developing application with multiple look and feel, I strongly
  suggest using this convention, since it cleanly separates concerns.


* Both support inheritance/acquisition

This is realized through a combination of interface inheritance and
component lookup techniques. We will discuss this in more detail
later.

Skins are directly provided by a request

Core Skins
----------

* Access skin using ++skin++Name after the server root

* Core Skins that are part of the repository

  - Rotterdam -- the default skin shown

  - Boston -- a newer skin featuring viewlets

  - Basic -- a skin with no layout styles

  - Debug -- based on Rotterdam, shows debug information upon
    failures

* Try http://localhost:8080/++skin++Boston

Unfortunately, it is hard to reuse the UI components developed for
these skins, since they still rely on the not so flexible macro
pattern. Thus, it is better if you start from scratch. This will also
avoid a lot of the overhead that comes with the over-generalized core
skins.

A New Skin
----------

* Views registered for default layer by default
  zope.publisher.interfaces.browser.IDefaultBrowserLayer

* Default layer contains a lot of things we do not need (security
  concerns)

* Since pretty much everything in zope.app is registered into the
  default layer, it has an uncontrollable amount of junk in it. It is
  very hard to verify that all those registrations fulfill your
  security needs. Another problem is that views might be available
  that you do not want to be available.


* Always want to develop skins from scratch

* Some registrations in the default layer are very useful

* Examples of those useful registrations include error views, traversal registrations, and widgets.

* Useful set of registrations collected in the minimal layer z3c.layer.minimal

* Add the z3c.layer.minimal package to your project dependencies


Setting up a Layer
------------------

Write an interface for the layer that inherits the minimal layer::

  from z3c.layer import minimal

  class IHelloWorldLayer(minimal.IMinimalBrowserLayer):
      """Hello World Application Layer"""


Change all page, viewletmanager, and viewlet directives to specify
this layer:

  layer=".interfaces.IHelloWorldLayer"

Once you changed those registrations, the helloworld.html page is not
available anymore in the core skins. The templates by themselves do
not matter.


Setting up a Skin
~~~~~~~~~~~~~~~~~

Write an interface for each new skin that inherits the Hello World
application layer::

      class IBasicSkin(IHelloWorldLayer):
          """Basic Skin for Hello World App."""

Register the interface as a skin interface::

  <zope:interface
      interface=".interfaces.IBasicSkin"
      type="zope.publisher.interfaces.browser.IBrowserSkinType"
      name="HWBasic"
      />

Register all templates for this skin by adding the layer attribute:

      layer=".interfaces.IBasicSkin"


Using the Skin
~~~~~~~~~~~~~~

Access it via: http://localhost:8080/++skin++HWBasic

Hide skin traversal step by using Apache's Virtual Hosting feature

To change the default skin to something else use:

  <browser:defaultSkin name="HWBasic" />

Simply specifying the browser:defaultSkin directive in your
configuration file will not work, since it has been specified in
zope/app/zcmlfiles/browser.zcml already. You can either change the
skin at this location or use the zope:includeOverrides directive,
which will override the any included directives.

Exercise
--------

* Develop the Hello World application layer.

* Develop two skins based on this layer.

* Write some tests that specifically test the difference between the
  skins.

================================
Conventions for Zope 3 Templates
================================

As the number of skins and usages of skins multiply in Zope 3, we need
to specificy some common patterns and conventions to make sure things
work together.  This document describes the problems that are being
addressed, lists the existing conventions, and proposes a new "usage"
top-level variable to promote template re-use.

Audience
--------

The primary audience of this proposal is Zope 3 framework and product
developers that create templates as a part of views and skins.  This
audience needs:

- Explanation of UI elements, their location, and what they can count
  on as "official"

- Improved facilities for the process of generically pluggable user
  interfaces

The second audience is the "non-core" group that will want to assemble
sites and do site development.  The composition of the user interface
needs to be clear and documented.

Goals
-----

This document and proposal has the following goals:

- Allow the template writers for skins and the template writers for
  products to work together.  When someone creates a skin (such as
  Rotterdam or Basic), they are imposing a certain structure on views
  that appear through that skin.  If a product doesn't adhere to that
  structure, bad things happen.  This proposal writes down the
  structure for the built-in skins.

- Ensure that products work in multiple skins.  In a small show this
  is easy, as everyone can adopt the same conventions.  When plugging
  together user interfaces, though, we need the moral equivalent of
  object interfaces.

- Promote targeted skins (specific to content manager, specific to
  site visitor, etc.) without forking the "global" structure.  The
  decision to improve the UI experience should not lead to a complete
  divorce from existing template work.

Topics
------

Skins, Layers, Masters, and Themes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Zope 3 skin is a collection of resources that define a page
structure, behavior, and style.  While the skin doesn't literally
contain all the templates for all the views of all the objects, it
*is* the governing template for all those templates.  Those templates
fill slots defined in the skin and use macros from the skin.

Skins introduce the concept of layers, which are collections of skin
resources for a targeted use.  Layers give a finer granularity to skin
composition, thus providing two major benefits:

- Template updates and changes are specific in scope and thus easier
  to manage

- Greater reuse between skins, as you can compose a skin by picking
  and choosing where you get your templates and resources from

Layers can be focused on different purposes.  For instance, some
layers provide the structure and behavior for all pages on a site.
For example, a layer might put the major boxes on a page, provide
important JavaScript handlers, and define macro pages.  Another type
of layer might focus on only on the look of the site.

It's important to classify these two kinds of layers, as one has more
repercussions than the other.  The structural layer, which we propose
to call a "master" layer, defines a regime of structure that all
templates rendered under that skin must be aware of.  The stylistic
layer, which we propose to call a "theme" layer, shouldn't break any
templates as it imposes no such regime.

Masters
~~~~~~~

- Skins = Masters + Themes + (other layers)

  - Masters are structure + behavior

  - Need: site developer skin, content manager skin, site visitor skin

- What you write for an application

- Unique master template 

The Usage Variable
~~~~~~~~~~~~~~~~~~

A skin must manage structural elements like navigation, tabs, location
breadcrumbs... Skin pages need to show all or some of those elements.

- An object view (as in the Rotterdam skin) has a lot of those
  structural elements.

- In dialog-style pages, you don't want elements such as tabs, menus,
  and the location bar.

- For the screen used in adding a new item, you also want many items
  to disappear, but also to add some information specific to this
  screen.

- In error dialogs, the location bar doesn't work, because errors have
  no location.

One option is to manage multiple versions of the master template and
applying them as whole-page macros on the various pages.  But multiple
master templates is cumbersome and error-prone.

To solve this, the skin facility introduces a top-level TAL variable
called 'usage'. The usage variable is there to allow you to maintain a
unique template for a whole application. This variable has a value
that sets different modes of operation. By testing usage, you can
decide which blocks should be shown or hidden when rendering the
template.

Having a unique template eases to enforce a coherent UI and consistent
look and feel by ensuring that structural elements do not move too
much on the screen.

The main way to set the value of 'usage' for a page is through the
menu it is registered to. A menu is a set of conceptually related
links to pages. When you click on one of those links, you should
arrive to about the same type of UI with identical (or at least
similar) information available. Getting usage from the menu will
enforce (we hope) the coherence of the UI. Actually, if a page is
registered to a menu, its usage value gets set from the usage value
set on the menu through its ZCML directive.

Anyway, usage can be overridden by initializing it through the page
configuration (ZCML directive).

The values of the 'usage' are chosen to describe broad categories
rather than individual templates or elements.  These are the proposed
values:

- 'usage/objectview' is the usage when browsing contents.  Example:
  folder contents.

- 'usage/activitydialog' is the usage when you are modifying an object
  in any way.  Example: rename.

- 'usage/error' is self-explanatory.

- 'usage/addingdialog' is used during the process of adding a new
  item.

Those values must be registered through the ``<browser:usage
name="usagevalue" />`` ZCML directive.

The following directives share the usage attribute:

- browser:menu

- browser:view

- browser:pages

- browser:page

- browser:editform

- browser:subeditform

- browser:editwizard

- browser:addform

- browser:addwizard

- browser:schemadisplay

The usage attribute can only be set as one of the registered usage values.

As an example, the 'template.pt' master template in the 'rotterdam'
skin has the following block::

  <div tal:condition="usage/objectview" 
       tal:repeat="structure view/tabs"></div>

- Themes are style, look and feel

- Slot conventions


Open Questions
--------------

- Multiple dimensions (preferences, etc.)

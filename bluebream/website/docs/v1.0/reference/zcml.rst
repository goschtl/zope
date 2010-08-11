ZCML Reference
==============

Introduction
------------

Zope Configuration Markup Language (ZCML) is the configuration
launguage used by BlueBream for all registrations.  ZCML is based on
XML.  BlueBream has many ZCML directives defined in various modules.
To use a particular ZCML directive, you need to include the package
distribution where the module is available. This document provides
reference to all ZCML directives provided by BlueBream.

Using ZCML Directives
---------------------

To use ZCML directive, you need to include the package distribution
as a dependency for your project.  Also you need to include the
module from the ``site.zcml`` file.

ZCML Directive Chart
--------------------

============================  ===========  =============================
ZCML Directive                Namspace     Module
============================  ===========  =============================
form                          browser      zope.app.form.browser
form/widget                   browser      zope.app.form.browser
editform                      browser      zope.app.form.browser
editform/widget               browser      zope.app.form.browser
subeditform                   browser      zope.app.form.browser
subeditform/widbrowserget     browser      zope.app.form.browser
addform                       browser      zope.app.form.browser
addform/widget                browser      zope.app.form.browser
schemadisplay                 browser      zope.app.form.browser
schemadisplay/widget          browser      zope.app.form.browser
view                          xmlrpc       zope.app.publisher.xmlrpc
defaultView                   browser      zope.publisher
defaultSkin                   browser      zope.publisher
publisher                     zope         zope.app.publication
containerViews                browser      zope.app.container.browser
permission                    zope         zope.security
securityPolicy                zope         zope.security
redefinePermission            zope         zope.security
class                         zope         zope.security
class/implements              zope         zope.security
class/require                 zope         zope.security
class/allow                   zope         zope.security
class/factory                 zope         zope.security
module                        zope         zope.security
module/allow                  zope         zope.security
module/require                zope         zope.security
register                      help         zope.app.onlinehelp
resourceLibrary               zope         zc.resourcelibrary
resourceLibrary/directory     zope         zc.resourcelibrary
menu                          zope         zope.browsermenu
menuItems                     zope         zope.browsermenu
menuItems/menuItem            zope         zope.browsermenu
menuItems/subMenuItem         zope         zope.browsermenu
menuItem                      zope         zope.browsermenu
subMenuItem                   zope         zope.browsermenu
addMenuItem                   zope         zope.browsermenu
interface                     zope         zope.component
adapter                       zope         zope.component
subscriber                    zope         zope.component
view                          zope         zope.component
resource                      zope         zope.component
page                          browser      zope.browserpage
pages                         browser      zope.browserpage
pages/page                    browser      zope.browserpage
view                          browser      zope.browserpage
view/page                     browser      zope.browserpage
defaultPage                   browser      zope.browserpage
expressiontype                tales        zope.app.pagetemplate
registerTranslations          i18n         zope.i18n
provideInterface              dav          zope.app.dav
viewlet                       browser      zope.viewlet
viewletManager                browser      zope.viewlet
codec                         zope         zope.mimetype
codec/charset                 zope         zope.mimetype
mimeTypes                     zope         zope.mimetype
queuedDelivery                mail         zope.sendmail
directDelivery                mail         zope.sendmail
smtpMailer                    mail         zope.sendmail
grant                         zope         zope.securitypolicy
grantAll                      zope         zope.securitypolicy
preferenceGroup               zope         zope.app.preference
bookchapter                   apidoc       zope.app.apidoc.bookmodule
moduleImport                  apidoc       zope.app.apidoc.codemodule
rootModule                    apidoc       zope.app.apidoc.codemodule
modulealias                   zope         zope.modulealias
principal                     zope         zope.principalregistry
unauthenticatedPrincipal      zope         zope.principalregistry
unauthenticatedGroup          zope         zope.principalregistry
authenticatedGroup            zope         zope.principalregistry
everybodyGroup                zope         zope.principalregistry
resource                      browser      zope.browserresource
resourceDirectory             browser      zope.browserresource
i18n-resource                 browser      zope.browserresource
i18n-resource/translation     browser      zope.browserresource
icon                          browser      zope.browserresource
provideConnection             rdb          zope.rdb
gadflyRoot                    rdb          zope.rdb
============================  ===========  =============================

- Note 1: The sub-directive is denoted like ``form/widget`` in the
  ZCML Directive column.

- Note 2: The value given in the namespace column is the suffix of
  actual XML namespace.  For example ``browser`` should be read as
  ``http://namespaces.zope.org/browser``.


form
----

:directive: ``form``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``<include package="zope.app.form.browser" />``
:distribution: ``zope.app.form``

**Description**

**Attributes**

**Sub-directives**

**Examples**

**Alternatives**

**See Also**

form/widget
-----------

:directive: ``form``
:sub-directive: ``widget``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

editform
--------

:directive: ``editform``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

editform/widget
---------------

:directive: ``editform``
:sub-directive: ``widget``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

subeditform
-----------

:directive: ``subeditform``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

subeditform/widbrowserget
-------------------------

:directive: ``subeditform``
:sub-directive: ``widget``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

addform
-------

:directive: ``addform``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

addform/widget
--------------

:directive: ``addform``
:sub-directive: ``widget``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**


schemadisplay
-------------

:directive: ``schemadisplay``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

schemadisplay/widget
--------------------

:directive: ``schemadisplay``
:sub-directive: ``widget``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

view
----

:directive: ``view``
:namespace: ``http://namespaces.zope.org/xmlrpc``
:include: ``zope.app.publisher.xmlrpc``
:distribution: ``zope.app.publisher``

**Examples**

defaultView
-----------

:directive: ``defaultView``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.publisher``

**Examples**

defaultSkin
-----------

:directive: ``defaultSkin``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.publisher``

**Examples**

publisher
---------

:directive: ``publisher``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.app.publication``

**Examples**

containerViews
--------------

:directive: ``containerViews``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.app.container.browser``
:distribution: ``zope.app.container``

**Examples**

permission
----------

:directive: ``permission``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

securityPolicy
--------------

:directive: ``securityPolicy``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

redefinePermission
------------------

:directive: ``redefinePermission``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

class
-----

:directive: ``class``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

class/implements
----------------

:directive: ``class``
:sub-directive: ``implements``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

class/require
-------------

:directive: ``class``
:sub-directive: ``require``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

class/allow
-----------

:directive: ``class``
:sub-directive: ``allow``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

class/factory
-------------

:directive: ``class``
:sub-directive: ``factory``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

module
------

:group-directive: ``module``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

module/allow
------------

:group-directive: ``module``
:directive: ``allow``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

module/require
--------------

:group-directive: ``module``
:directive: ``require``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.security``

**Examples**

register
--------

:directive: ``register``
:namespace: ``http://namespaces.zope.org/help``
:include: ``zope.app.onlinehelp``

**Examples**

resourceLibrary
---------------

:directive: ``resourceLibrary``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zc.resourcelibrary``

**Examples**

resourceLibrary/directory
-------------------------

:directive: ``resourceLibrary``
:sub-directive: ``directory``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zc.resourcelibrary``

**Examples**

menu
----

:directive: ``menu``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.browsermenu``

**Examples**

menuItems
---------

:directive: ``menuItems``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.browsermenu``

**Examples**

menuItems/menuItem
------------------

:directive: ``menuItems``
:sub-directive: ``menuItem``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.browsermenu``

**Examples**

menuItems/subMenuItem
---------------------

:directive: ``menuItems``
:sub-directive: ``subMenuItem``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.browsermenu``

**Examples**

menuItem
--------

:directive: ``menuItem``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.browsermenu``

**Examples**

subMenuItem
-----------

:directive: ``subMenuItem``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.browsermenu``

**Examples**

addMenuItem
-----------

:directive: ``addMenuItem``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.browsermenu``

**Examples**

interface
---------

:directive: ``interface``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.component``

**Examples**

adapter
-------

:directive: ``adapter``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.component``

**Examples**

subscriber
----------

:directive: ``subscriber``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.component``

**Examples**

view
----

:directive: ``view``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.component``

**Examples**

resource
--------

:directive: ``resource``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.component``

**Examples**

page
----

:directive: ``browser:page``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserpage``
:distribution: ``zope.browserpage``

**Attributes**

- **for** - Specifications of the objects to be viewed.

  This should be a list of interfaces or classes.

- ``permission`` - Permission

  The permission needed to use the view.

- ``class`` - Class

  A class that provides attributes used by the view.

- ``layer`` - The layer the view is in.

  A skin is composed of layers.  It is common to put skin specific
  views in a layer named after the skin.  If the ``layer`` attribute
  is not supplied, it defaults to ``default``.

- ``allowed_interface`` - Interface that is also allowed if user has
  permission.

  By default, ``permission`` only applies to viewing the view and any
  possible sub views.  By specifying this attribute, you can make the
  permission also apply to everything described in the supplied
  interface.

  Multiple interfaces can be provided, separated by whitespace.

- ``allowed_attributes`` - View attributes that are also allowed if
  the user has permission

  By default, ``permission`` only applies to viewing the view and any
  possible sub views.  By specifying ``allowed_attributes``, you can
  make the permission also apply to the extra attributes on the view
  object

- **name** - The name of the page (view)

  The name shows up in URLs/paths.  For example ``foo`` or
  ``foo.html``. This attribute is required unless you use the
  subdirective ``page`` to create sub views.  If you do not have sub
  pages, it is common to use an extension for the view name such as
  ``.html``.  If you do have sub pages and you want to provide a view
  name, you shouldn't use extensions.

- ``attribute`` - The name of the view attribute implementing the page.

  This refers to the attribute (method) on the view that is
  implementing a specific sub page.

- ``template`` - The name of a template that implements the page.

  Refers to a file containing a page template (should end in
  extension ``.pt`` or ``.html``.

- ``menu`` - The browser menu to include the page (view) in.

  Many views are included in menus.  It's convenient to name the menu
  in the page directive, rather than having to give a separate
  menuItem directive.

  This attribute will only work if zope.browsermenu is installed.

- ``title`` - The browser menu label for the page (view)

  This attribute must be supplied if a menu attribute is supplied.

  This attribute will only work if *zope.browsermenu* is installed.

**Examples**

pages
-----

:directive: ``pages``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserpage``

**Examples**

pages/page
----------

:directive: ``pages``
:sub-directive: ``page``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserpage``

**Examples**

view
----

:directive: ``view``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserpage``

**Examples**

view/page
---------

:directive: ``view``
:sub-directive: ``page``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserpage``

**Examples**

defaultPage
-----------

:directive: ``view``
:sub-directive: ``defaultPage``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserpage``

**Examples**

expressiontype
--------------

:directive: ``expressiontype``
:namespace: ``http://namespaces.zope.org/tales``
:include: ``zope.browserpage``

**Examples**

registerTranslations
--------------------

:directive: ``registerTranslations``
:namespace: ``http://namespaces.zope.org/i18n``
:include: ``zope.i18n``

**Examples**

provideInterface
----------------

:directive: ``provideInterface``
:namespace: ``http://namespaces.zope.org/dav``
:include: ``zope.app.dav``

**Examples**

viewlet
-------

:directive: ``viewlet``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.viewlet``

**Examples**

viewletManager
--------------

:directive: ``viewletManager``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.viewlet``

**Examples**

codec
-----

:directive: ``codec``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.mimetype``

**Examples**

codec/charset
-------------

:directive: ``codec``
:sub-directive: ``charset``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.mimetype``

**Examples**

mimeTypes
---------

:directive: ``mimeTypes``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.mimetype``

**Examples**

queuedDelivery
--------------

:directive: ``queuedDelivery``
:namespace: ``http://namespaces.zope.org/mail``
:include: ``zope.sendmail``

**Examples**

directDelivery
--------------

:directive: ``directDelivery``
:namespace: ``http://namespaces.zope.org/mail``
:include: ``zope.sendmail``

**Examples**

smtpMailer
----------

:directive: ``smtpMailer``
:namespace: ``http://namespaces.zope.org/mail``
:include: ``zope.sendmail``

**Examples**

grant
-----

:directive: ``grant``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.securitypolicy``

**Examples**

grantAll
--------

:directive: ``grantAll``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.securitypolicy``

**Examples**

preferenceGroup
---------------

:directive: ``preferenceGroup``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.app.preference``

**Examples**

bookchapter
-----------

:directive: ``bookchapter``
:namespace: ``http://namespaces.zope.org/apidoc``
:include: ``zope.app.apidoc.bookmodule``
:distribution: ``zope.app.apidoc``

**Examples**

moduleImport
------------

:directive: ``moduleImport``
:namespace: ``http://namespaces.zope.org/apidoc``
:include: ``zope.app.apidoc.codemodule``
:distribution: ``zope.app.apidoc``

**Examples**

rootModule
----------

:directive: ``rootModule``
:namespace: ``http://namespaces.zope.org/apidoc``
:include: ``zope.app.apidoc.codemodule``
:distribution: ``zope.app.apidoc``

**Examples**

modulealias
-----------

:directive: ``modulealias``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.modulealias``

**Examples**

principal
---------

:directive: ``principal``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.principalregistry``

**Examples**

unauthenticatedPrincipal
------------------------

:directive: ``unauthenticatedPrincipal``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.principalregistry``

**Examples**

unauthenticatedGroup
--------------------

:directive: ``unauthenticatedGroup``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.principalregistry``

**Examples**

authenticatedGroup
------------------

:directive: ``authenticatedGroup``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.principalregistry``

**Examples**

everybodyGroup
--------------

:directive: ``everybodyGroup``
:namespace: ``http://namespaces.zope.org/zope``
:include: ``zope.principalregistry``

**Examples**

resource
--------

:directive: ``browser:resource``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserresource``
:distribution: ``zope.browserresource``

**Description**

Certain presentation, like images and style sheets are not associated
with any other component, so that one cannot create a view.  To solve
this problem, resources were developed, which are presentation
components that do not require any context.

**Attributes**

- **name** - The name of the resource

  This is the name used in resource urls. Resource urls are of the
  form ``site/@@/resourcename``, where site is the url of ``site``, a
  folder with a site manager.

  We make resource urls site-relative (as opposed to
  content-relative) so as not to defeat caches.

- ``factory`` - Resource Factory

  The factory used to create the resource. The factory should only
  expect to get the request passed when called.

- ``file`` - File

  The file containing the resource data.


- ``image`` - Image

  If the image attribute is used, then an image resource, rather than
  a file resource will be created.

- ``layer`` - The layer the resource should be found in

  For information on layers, see the documentation for the skin
  directive.  Defaults to *default*.

- ``permission`` - The permission needed to access the resource.

  If a permission isn't specified, the resource will always be
  accessible.

- ``template`` - Template

  If the template attribute is used, then a page template resource,
  rather than a file resource will be created.

**Examples**

::

  <browser:resource
      name="resource.txt"
      file="resource.txt"
      layer="default" />

Once you hook up the configuration file to the main configuration
path and restart BlueBream, you should be able to access the resource
now via a Browser at: http://localhost:8080/@@/resource.txt.  The
``@@/`` in the URL tells the traversal mechanism that the following
object is a resource.

**See Also**

- `resourceDirectory`_

resourceDirectory
-----------------

:directive: ``resourceDirectory``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserresource``

**Description**

**Attributes**

- **name** - The name of the resource

  This is the name used in resource urls. Resource urls are of the
  form ``site/@@/resourcename``, where site is the url of ``site``, a
  folder with a site manager.

  We make resource urls site-relative (as opposed to
  content-relative) so as not to defeat caches.

- **directory** - Directory

  The directory containing the resource data.

- ``factory`` - Resource Factory

  The factory used to create the resource. The factory should only
  expect to get the request passed when called.

- ``file`` - File

  The file containing the resource data.


- ``image`` - Image

  If the image attribute is used, then an image resource, rather than
  a file resource will be created.

- ``layer`` - The layer the resource should be found in

  For information on layers, see the documentation for the skin
  directive.  Defaults to *default*.

- ``permission`` - The permission needed to access the resource.

  If a permission isn't specified, the resource will always be
  accessible.

- ``template`` - Template

  If the template attribute is used, then a page template resource,
  rather than a file resource will be created.

**Examples**

::

  <browser:resourceDirectory
    name="resource"
    directory="resource"
    />

i18n-resource
-------------

:directive: ``i18n-resource``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserresource``

**Examples**

i18n-resource/translation
-------------------------

:directive: ``i18n-resource``
:sub-directive: ``translation``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserresource``

**Examples**

icon
----

:directive: ``icon``
:namespace: ``http://namespaces.zope.org/browser``
:include: ``zope.browserresource``

**Examples**

provideConnection
-----------------

:directive: ``provideConnection``
:namespace: ``http://namespaces.zope.org/rdb``
:include: ``zope.rdb``

This directive and ``zope.rdb`` is not actively used by the community.  If
you want relational database connectivily, look at `z3c.sqlalchemy
<http://pypi.python.org/pypi/z3c.sqlalchemy>`_.

gadflyRoot
----------

:directive: ``gadflyRoot``
:namespace: ``http://namespaces.zope.org/rdb``
:include: ``zope.rdb``

This directive and ``zope.rdb`` is not actively used by the community.  If
you want relational database connectivily, look at `z3c.sqlalchemy
<http://pypi.python.org/pypi/z3c.sqlalchemy>`_.


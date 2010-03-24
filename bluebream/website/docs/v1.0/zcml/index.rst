ZCML Reference
==============

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.

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
:module: ``zope.app.form.browser``
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
:module: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

editform
--------

:directive: ``editform``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

editform/widget
---------------

:directive: ``editform``
:sub-directive: ``widget``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

subeditform
-----------

:directive: ``subeditform``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

subeditform/widbrowserget
-------------------------

:directive: ``subeditform``
:sub-directive: ``widget``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

addform
-------

:directive: ``addform``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

addform/widget
--------------

:directive: ``addform``
:sub-directive: ``widget``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**


schemadisplay
-------------

:directive: ``schemadisplay``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

schemadisplay/widget
--------------------

:directive: ``schemadisplay``
:sub-directive: ``widget``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.app.form.browser``
:distribution: ``zope.app.form``

**Examples**

view
----

:directive: ``view``
:namespace: ``http://namespaces.zope.org/xmlrpc``
:module: ``zope.app.publisher.xmlrpc``
:distribution: ``zope.app.publisher``

**Examples**

defaultView
-----------

:directive: ``defaultView``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.publisher``

**Examples**

defaultSkin
-----------

:directive: ``defaultSkin``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.publisher``

**Examples**

publisher
---------

:directive: ``publisher``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.app.publication``

**Examples**

containerViews
--------------

:directive: ``containerViews``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.app.container.browser``
:distribution: ``zope.app.container``

**Examples**

permission
----------

:directive: ``permission``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

securityPolicy
--------------

:directive: ``securityPolicy``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

redefinePermission
------------------

:directive: ``redefinePermission``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

class
-----

:directive: ``class``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

class/implements
----------------

:directive: ``class``
:sub-directive: ``implements``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

class/require
-------------

:directive: ``class``
:sub-directive: ``require``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

class/allow
-----------

:directive: ``class``
:sub-directive: ``allow``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

class/factory
-------------

:directive: ``class``
:sub-directive: ``factory``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

module
------

:group-directive: ``module``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

module/allow
------------

:group-directive: ``module``
:directive: ``allow``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

module/require
--------------

:group-directive: ``module``
:directive: ``require``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.security``

**Examples**

register
--------

:directive: ``register``
:namespace: ``http://namespaces.zope.org/help``
:module: ``zope.app.onlinehelp``

**Examples**

resourceLibrary
---------------

:directive: ``resourceLibrary``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zc.resourcelibrary``

**Examples**

resourceLibrary/directory
-------------------------

:directive: ``resourceLibrary``
:sub-directive: ``directory``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zc.resourcelibrary``

**Examples**

menu
----

:directive: ``menu``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.browsermenu``

**Examples**

menuItems
---------

:directive: ``menuItems``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.browsermenu``

**Examples**

menuItems/menuItem
------------------

:directive: ``menuItems``
:sub-directive: ``menuItem``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.browsermenu``

**Examples**

menuItems/subMenuItem
---------------------

:directive: ``menuItems``
:sub-directive: ``subMenuItem``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.browsermenu``

**Examples**

menuItem
--------

:directive: ``menuItem``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.browsermenu``

**Examples**

subMenuItem
-----------

:directive: ``subMenuItem``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.browsermenu``

**Examples**

addMenuItem
-----------

:directive: ``addMenuItem``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.browsermenu``

**Examples**

interface
---------

:directive: ``interface``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.component``

**Examples**

adapter
-------

:directive: ``adapter``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.component``

**Examples**

subscriber
----------

:directive: ``subscriber``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.component``

**Examples**

view
----

:directive: ``view``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.component``

**Examples**

resource
--------

:directive: ``resource``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.component``

**Examples**

page
----

:directive: ``page``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserpage``

**Examples**

pages
-----

:directive: ``pages``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserpage``

**Examples**

pages/page
----------

:directive: ``pages``
:sub-directive: ``page``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserpage``

**Examples**

view
----

:directive: ``view``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserpage``

**Examples**

view/page
---------

:directive: ``view``
:sub-directive: ``page``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserpage``

**Examples**

defaultPage
-----------

:directive: ``view``
:sub-directive: ``defaultPage``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserpage``

**Examples**

expressiontype
--------------

:directive: ``expressiontype``
:namespace: ``http://namespaces.zope.org/tales``
:module: ``zope.app.pagetemplate``

**Examples**

registerTranslations
--------------------

:directive: ``registerTranslations``
:namespace: ``http://namespaces.zope.org/i18n``
:module: ``zope.i18n``

**Examples**

provideInterface
----------------

:directive: ``provideInterface``
:namespace: ``http://namespaces.zope.org/dav``
:module: ``zope.app.dav``

**Examples**

viewlet
-------

:directive: ``viewlet``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.viewlet``

**Examples**

viewletManager
--------------

:directive: ``viewletManager``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.viewlet``

**Examples**

codec
-----

:directive: ``codec``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.mimetype``

**Examples**

codec/charset
-------------

:directive: ``codec``
:sub-directive: ``charset``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.mimetype``

**Examples**

mimeTypes
---------

:directive: ``mimeTypes``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.mimetype``

**Examples**

queuedDelivery
--------------

:directive: ``queuedDelivery``
:namespace: ``http://namespaces.zope.org/mail``
:module: ``zope.sendmail``

**Examples**

directDelivery
--------------

:directive: ``directDelivery``
:namespace: ``http://namespaces.zope.org/mail``
:module: ``zope.sendmail``

**Examples**

smtpMailer
----------

:directive: ``smtpMailer``
:namespace: ``http://namespaces.zope.org/mail``
:module: ``zope.sendmail``

**Examples**

grant
-----

:directive: ``grant``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.securitypolicy``

**Examples**

grantAll
--------

:directive: ``grantAll``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.securitypolicy``

**Examples**

preferenceGroup
---------------

:directive: ``preferenceGroup``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.app.preference``

**Examples**

bookchapter
-----------

:directive: ``bookchapter``
:namespace: ``http://namespaces.zope.org/apidoc``
:module: ``zope.app.apidoc.bookmodule``
:distribution: ``zope.app.apidoc``

**Examples**

moduleImport
------------

:directive: ``moduleImport``
:namespace: ``http://namespaces.zope.org/apidoc``
:module: ``zope.app.apidoc.codemodule ``
:distribution: ``zope.app.apidoc``

**Examples**

rootModule
----------

:directive: ``rootModule``
:namespace: ``http://namespaces.zope.org/apidoc``
:module: ``zope.app.apidoc.codemodule ``
:distribution: ``zope.app.apidoc``

**Examples**

modulealias
-----------

:directive: ``modulealias``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.modulealias``

**Examples**

principal
---------

:directive: ``principal``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.principalregistry``

**Examples**

unauthenticatedPrincipal
------------------------

:directive: ``unauthenticatedPrincipal``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.principalregistry``

**Examples**

unauthenticatedGroup
--------------------

:directive: ``unauthenticatedGroup``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.principalregistry``

**Examples**

authenticatedGroup
------------------

:directive: ``authenticatedGroup``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.principalregistry``

**Examples**

everybodyGroup
--------------

:directive: ``everybodyGroup``
:namespace: ``http://namespaces.zope.org/zope``
:module: ``zope.principalregistry``

**Examples**

resource
--------

:directive: ``resource``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserresource``

**Examples**

resourceDirectory
-----------------

:directive: ``resourceDirectory``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserresource``

**Examples**

i18n-resource
-------------

:directive: ``i18n-resource``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserresource``

**Examples**

i18n-resource/translation
-------------------------

:directive: ``i18n-resource``
:sub-directive: ``translation``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserresource``

**Examples**

icon
----

:directive: ``icon``
:namespace: ``http://namespaces.zope.org/browser``
:module: ``zope.browserresource``

**Examples**

provideConnection
-----------------

:directive: ``provideConnection``
:namespace: ``http://namespaces.zope.org/rdb``
:module: ``zope.rdb``

**Examples**

gadflyRoot
----------

:directive: ``gadflyRoot``
:namespace: ``http://namespaces.zope.org/rdb``
:module: ``zope.rdb``

**Examples**


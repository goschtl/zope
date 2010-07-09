Package Usage
=============

These tables show which packages are used by which frameworks. Plone is
included for reference only.

The following abbreviations are used in the table:

B = BlueBream
G = Grok
2 = Zope 2.13.0a1
P = Plone (4.0b4 with Zope 2.13.0a1)

x = is used
_ = is not used

We do not differentiate the type of dependency (direct or transitive). At this
point we are only interested if a package is required by a framework in some
way or not.

In a ``zopepy`` interpreter one can get all active distributions with::

  import pprint, pkg_resources
  pprint.pprint(sorted([p.project_name for p in pkg_resources.working_set.by_key.values()]))

ZTK
---

= = = = =============================
B G 2 P Package name
= = = = =============================
x x x x zope.annotation
x _ _ _ zope.applicationcontrol
x x _ x zope.authentication
x x x x zope.broken
x x x x zope.browser
x x x x zope.browsermenu
x x x x zope.browserpage
x x x x zope.browserresource
x x _ x zope.cachedescriptors
_ x _ _ zope.catalog
x x x x zope.component
x x _ x zope.componentvocabulary
x x x x zope.configuration
x x x x zope.container
_ x x x zope.contentprovider
x x x x zope.contenttype
x x _ x zope.copy
x x _ x zope.copypastemove
x x _ x zope.datetime
x x x x zope.deferredimport
x x _ x zope.deprecation
_ _ _ _ zope.documenttemplate
x x x x zope.dottedname
x x _ x zope.dublincore
x x _ x zope.error
x x x x zope.event
x x x x zope.exceptions
x x x x zope.filerepresentation
x x _ x zope.formlib
x x _ x zope.hookable
x x x x zope.i18n
x x x x zope.i18nmessageid
_ x _ _ zope.index
x x x x zope.interface
_ x _ _ zope.intid
_ x _ _ zope.keyreference
x x x x zope.lifecycleevent
x x x x zope.location
x x _ x zope.login
_ _ _ _ zope.mimetype
x x _ x zope.minmax
x x x x zope.pagetemplate
x x _ x zope.password
x x _ x zope.pluggableauth
x x _ _ zope.principalannotation
x x _ x zope.principalregistry
x x x x zope.processlifetime
x x x x zope.proxy
x x x x zope.ptresource
x x x x zope.publisher
_ _ _ x zope.ramcache
x x x x zope.schema
x x x x zope.security
x x _ x zope.securitypolicy
_ _ x x zope.sendmail
_ _ x x zope.sequencesort
_ _ _ _ zope.server
x x _ x zope.session
x x x x zope.site
x x x x zope.size
x x x x zope.structuredtext
x x x x zope.tal
x x x x zope.tales
x x x x zope.testing
x x x x zope.traversing
_ x x x zope.viewlet
= = = = =============================

Zope App
--------

= = = = =============================
B G 2 P Package name
= = = = =============================
_ _ _ _ zope.app.apidoc
x x _ _ zope.app.applicationcontrol
x x _ _ zope.app.appsetup
x x _ x zope.app.authentication
x x _ _ zope.app.basicskin
x x _ _ zope.app.broken
_ _ _ x zope.app.cache
_ _ _ _ zope.app.catalog
x x _ x zope.app.component
x x _ x zope.app.container
x x _ x zope.app.content
_ _ _ _ zope.app.dav
x x _ _ zope.app.debug
_ _ _ _ zope.app.debugskin
x x _ _ zope.app.dependable
x x _ _ zope.app.error
x x _ _ zope.app.exception
_ _ _ _ zope.app.file
x x _ x zope.app.folder
x x _ x zope.app.form
_ _ _ _ zope.app.ftp
x x _ _ zope.app.generations
x x _ _ zope.app.http
x x _ _ zope.app.i18n
x x _ x zope.app.interface
_ _ _ _ zope.app.interpreter
_ _ _ _ zope.app.intid
_ _ _ _ zope.app.keyreference
x x _ x zope.app.locales
x x _ x zope.app.localpermission
_ _ _ _ zope.app.locking
_ _ _ _ zope.app.onlinehelp
x x _ x zope.app.pagetemplate
_ _ _ _ zope.app.preference
_ _ _ _ zope.app.preview
x x _ _ zope.app.principalannotation
x x _ x zope.app.publication
x x _ x zope.app.publisher
x x _ _ zope.app.renderer
x x _ _ zope.app.rotterdam
x x _ _ zope.app.schema
x x _ x zope.app.security
_ _ _ _ zope.app.securitypolicy
_ _ _ _ zope.app.server
_ _ _ _ zope.app.session
_ _ _ _ zope.app.skins
x x _ _ zope.app.testing
_ _ _ _ zope.app.tree
_ _ _ _ zope.app.twisted
_ _ _ _ zope.app.undo
x x _ _ zope.app.wsgi
x x _ _ zope.app.zcmlfiles
x x _ _ zope.app.zopeappgenerations
_ _ _ _ zope.app.zptpage
_ _ _ _ zc.sourcefactory
x x _ x zodbcode
_ _ _ _ zope.file
_ _ _ _ zope.html
_ _ _ _ zope.modulealias
_ _ _ _ zope.preference
x x x x zope.testbrowser
_ _ _ _ zope.thread
_ _ _ _ zope.xmlpickle
_ _ _ _ zope.rdb
= = = = =============================

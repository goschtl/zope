Changelog
=========

This file contains change information for the current Zope release.
Change information for previous versions of Zope can be found in the
file HISTORY.txt.

Trunk (2009/05/06)
------------------

Restructuring
+++++++++++++

- No longer depend on `zope.app.locales`. Zope2 uses almost none of the
  translations provided in the package and is not required for most projects.
  The decision to include locales is left to the application developer now.

- Removed the dependency on `zope.app.testing` in favor of providing a more
  minimal placeless setup as part of ZopeTestCase for our own tests.

- updated to ZODB 3.9.0b1

Features Added
++++++++++++++

- Launchpad #375322: the <environment> section within the zope.conf
  file is now a multisection in order to provide a more modular configuration
  support.
  
- Launchpad #374729: Encoding cookie values to avoid issues with
  firewalls and security proxies.

- Launchpad #374719: introducing new ZPublisher events:
  PubStart, PubSuccess, PubFailure, PubAfterTraversal and PubBeforeCommit.

- Launchpad #373583: ZODBMountPoint - fixed broken mount support and 
  extended the test suite.

- Launchpad #373621: catching and logging exceptions that could cause
  leaking of worker threads.

- Launchpad #373577: setting up standard logging earlier within the startup
  phase for improving the analysis of startup errors.

- Launchpad #373601: abort transaction before connection close in order to
  prevent connection leaks in case of persistent changes after the main
  transaction is closed.

- zExceptions.convertExceptionType:  new API, breaking out conversion of
  exception names to exception types from 'upgradeException'.

- Extended BrowserIdManager to expose the 'HTTPOnly' attribute for its
  cookie. Also via https://bugs.launchpad.net/zope2/+bug/367393 .

- Added support for an optional 'HTTPOnly' attribute of cookies (see
  http://www.owasp.org/index.php/HTTPOnly).  Patch from Stephan Hofmockel,
  via https://bugs.launchpad.net/zope2/+bug/367393 .

Bugs Fixed
++++++++++

- RESPONSE.handle_errors was wrongly set (to debug, should have been
  ``not debug``). Also, the check for exception constructor arguments
  didn't account for exceptions that didn't override the ``__init__``
  (which are most of them). The combination of those two problems
  caused the ``standard_error_message`` not to be called. Fixes
  https://bugs.edge.launchpad.net/zope2/+bug/372632 .

- DocumentTemplate.DT_Raise:  use new 'zExceptions.convertExceptionType'
  API to allow raising non-builtin exceptions.
  Fixes https://bugs.launchpad.net/zope2/+bug/372629 , which prevented
  viewing the "Try" tab of a script with no parameters.

- ZPublisher response.setBody: don't append Accept-Encoding to Vary header if
  it is already present - this can make cache configuration difficult.

2.12.0a4 (2009-04-24)
---------------------

Bugs Fixed
++++++++++

- fixed versions.cfg in order to support zope.z2release for
  creating a proper index structure

2.12.0a3 (2009-04-19)
---------------------

The generated tarball for the 2.12.0a2 source release was incomplete, due to
a setuptools and Subversion 1.6 incompatibility.

Restructuring
+++++++++++++

- Added automatic inline migration for databases created with older Zope
  versions. The `Versions` screen from the `Control_Panel` is now
  automatically removed on Zope startup.

- Removed more unused code of the versions support feature including the
  Globals.VersionNameName constant.

2.12.0a2 (2009-04-19)
---------------------

Restructuring
+++++++++++++

- If the <permission /> ZCML directive is used to declare a permission that
  does not exist, the permission will now be created automatically, defaulting
  to being granted to the Manager role only. This means it is possible to
  create new permissions using ZCML only. The permission will Permissions that
  already exist will not be changed.

- Using <require set_schema="..." /> or <require set_attributes="..." /> in
  the <class /> directive now emits a warning rather than an error. The
  concept of protecting attribute 'set' does not exist in Zope 2, but it
  should be possible to re-use packages that do declare such protection.

- Updated to Acquisition 2.12.1.

- Updated to DateTime 2.12.0.

- Updated to ZODB 3.9.0a12.

- Removed the `getPackages` wrapper from setup.py which would force all
  versions to an exact requirement. This made it impossible to require
  newer versions of the dependencies. This kind of KGS information needs
  to be expressed in a different way.

- removed `extras_require` section from setup.py (this might possibly
  break legacy code).

Bugs Fixed
++++++++++

- Launchpad #348223: optimize catalog query by breaking out early from loop
  over indexes if the result set is already empty.

- Launchpad #344098: in ``skel/etc/zope.conf.ing``, replaced commented-out
  ``read-only-database`` option, which is deprecated, with pointers to the
  appropos sections of ZODB's ``component.xml``.  Updated the description
  of the ``zserver-read-only-mode`` directive to indicate its correct
  semantics (suppressing log / pid / lock files).  Added deprecation to the
  ``read-only-database`` option, which has had no effect since Zope 2.6.

- "Permission tab": correct wrong form parameter for
  the user-permission report

- PageTemplates: Made PreferredCharsetResolver work with new kinds of contexts
  that are not acquisition wrapped.

- Object managers should evaluate to True in a boolean test.

2.12.0a1 (2009-02-26)
---------------------

Restructuring
+++++++++++++

- Switched Products.PageTemplates to directly use zope.i18n.translate and
  removed the GlobalTranslationService hook.

- Removed bridging code from Product.Five for PlacelessTranslationService
  and Localizer. Neither of the two is actually using this anymore.

- Removed the specification of `SOFTWARE_HOME` and `ZOPE_HOME` from the
  standard instance scripts.
  [hannosch]

- Made the specification of `SOFTWARE_HOME` and `ZOPE_HOME` optional. In
  addition `INSTANCE_HOME` is no longer required to run the tests of a
  source checkout of Zope.

- Removed the `test` command from zopectl. The test.py script it was relying
  on does no longer exist.

- Updated to ZODB 3.9.0a11. ZODB-level version support has been
  removed and ZopeUndo now is part of Zope2.

- The Zope2 SVN trunk is now a buildout pulling in all dependencies as
  actual released packages and not SVN externals anymore.

- Make use of the new zope.container and zope.site packages.

- Updated to newer versions of zope packages. Removed long deprecated
  layer and skin ZCML directives.

- Disabled the XML export on the UI level - the export functionality
  however is still available on the Python level.

- No longer show the Help! links in the ZMI, if there is no help
  available. The help system depends on the product registry.

- Updated the quick start page and simplified the standard content.
  The default index_html is now a page template.

- Removed deprecated Draft and Version support from Products.OFSP.
  Also removed version handling from the control panel. Versions are
  no longer supported on the ZODB level.

- Removed left-overs of the deprecated persistent product distribution
  mechanism.

- The persistent product registry is not required for starting Zope
  anymore. `enable-product-installation` can be set to off if you don't
  rely on the functionality provided by the registry.

- ZClasses have been deprecated for two major releases. They have been
  removed in this version of Zope.

- Avoid deprecation warnings for the md5 and sha modules in Python 2.6
  by adding conditional imports for the hashlib module.

- Replaced imports from the 'Globals' module throughout the 
  tree with imports from the actual modules;  the 'Globals' module
  was always intended to be an area for shared data, rather than
  a "facade" for imports.  Added zope.deferred.deprecation entries
  to 'Globals' for all symbols / modules previously imported directly.

- Protect against non-existing zope.conf path and products directories.
  This makes it possible to run a Zope instance without a Products or
  lib/python directory.

- Moved exception MountedStorageError from ZODB.POSExceptions
  to Products.TemporaryFolder.mount (now its only client).

- Moved Zope2-specific module, ZODB/Mount.py, to
  Products/TemporaryFolder/mount.py (its only client is
  Products/TemporaryFolder/TemporaryFolder.py).

- Removed spurious import-time dependencies from
  Products/ZODBMountPoint/MountedObject.py.

- Removed Examples.zexp from the skeleton. The TTW shopping cart isn't
  any good example of Zope usage anymore.

- Removed deprecated ZTUtil.Iterator module

- Removed deprecated StructuredText module

- Removed deprecated TAL module

- Removed deprecated modules from Products.PageTemplates.

- Removed deprecated ZCML directives from Five including the whole
  Five.site subpackage.

Features added
++++++++++++++

- OFS.ObjectManager now fully implements the zope.container.IContainer
  interface. For the last Zope2 releases it already claimed to implement the
  interface, but didn't actually full-fill the interface contract. This means
  you can start using more commonly used Python idioms to access objects inside
  object managers. Complete dictionary-like access and container methods
  including iteration are now supported. For each class derived from
  ObjectManager you can use for any instance om: `om.keys()` instead of
  `om.objectIds()`, `om.values()` instead of `om.objectValues()`, but also
  `om.items()`, `ob.get('id')`, `ob['id']`, `'id' in om`, `iter(om)`,
  `len(om)`, `om['id'] = object()` instead of `om._setObject('id', object())`
  and `del ob['id']`. Should contained items of the object manager have ids
  equal to any of the new method names, the objects will override the method,
  as expected in Acquisition enabled types. Adding new objects into object
  managers by those new names will no longer work, though. The added methods
  call the already existing methods internally, so if a derived type overwrote
  those, the new interface will provide the same functionality.

- Acquisition has been made aware of `__parent__` pointers. This allows
  direct access to many Zope 3 classes without the need to mixin
  Acquisition base classes for the security to work.

- MailHost: now uses zope.sendmail for delivering the mail. With this
  change MailHost integrates with the Zope transaction system (avoids
  sending dupe emails in case of conflict errors). In addition
  MailHost now provides support for asynchronous mail delivery. The
  'Use queue' configuration option will create a mail queue on the
  filesystem (under 'Queue directory') and start a queue thread that
  checks the queue every three seconds. This decouples the sending of
  mail from its delivery.  In addition MailHosts now supports
  encrypted connections through TLS/SSL.

- SiteErrorLog now includes the entry id in the information copied to
  the event log. This allowes you to correlate a user error report with
  the event log after a restart, or let's you find the REQUEST
  information in the SiteErrorLog when looking at a traceback in the
  event log.

Bugs Fixed
++++++++++

- Launchpad #332168: Connection.py: do not expose DB connection strings
  through exceptions

- Specified height/width of icons in ZMI listings so the table doesn't
  jump around while loading.

- After the proper introduction of parent-pointers, it's now
  wrong to acquisition-wrap content providers. We will now use
  the "classic" content provider expression from Zope 3.

- Ported c69896 to Five. This fix makes it possible to provide a
  template using Python, and not have it being set to `None` by
  the viewlet manager directive.

- Made Five.testbrowser compatible with mechanize 0.1.7b.

- Launchpad #280334: Fixed problem with 'timeout'
  argument/attribute missing in testbrowser tests.

- Launchpad #267834: proper separation of HTTP header fields   
  using CRLF as requested by RFC 2616.

- Launchpad #257276: fix for possible denial-of-service attack
  in PythonScript when passing an arbitrary module to the encode()
  or decode() of strings.

- Launchpad #257269: 'raise SystemExit' with a PythonScript could shutdown
  a complete Zope instance

- Switch to branch of 'zope.testbrowser' external which suppresses
  over-the-wire tests.

- Launchpad #143902: Fixed App.ImageFile to use a stream iterator to
  output the file. Avoid loading the file content when guessing the
  mimetype and only load the first 1024 bytes of the file when it cannot
  be guessed from the filename.

- Changed PageTemplateFile not to load the file contents on Zope startup
  anymore but on first access instead. This brings them inline with the
  zope.pagetemplate version and speeds up Zope startup.

- Collector #2278: form ':record' objects did not implement enough
  of the mapping protocol.

- "version.txt" file was being written to the wrong place by the
  Makefile, causing Zope to report "unreleased version" even for
  released versions.

- Five.browser.metaconfigure.page didn't protect names from interface
  superclasses (http://www.zope.org/Collectors/Zope/2333)

- DAV: litmus "notowner_modify" tests warn during a MOVE request
  because we returned "412 Precondition Failed" instead of "423
  Locked" when the resource attempting to be moved was itself
  locked.  Fixed by changing Resource.Resource.MOVE to raise the
  correct error.

- DAV: litmus props tests 19: propvalnspace and 20:
  propwformed were failing because Zope did not strip off the
  xmlns: attribute attached to XML property values.  We now strip
  off all attributes that look like xmlns declarations.

- DAV: When a client attempted to unlock a resource with a token
  that the resource hadn't been locked with, in the past we
  returned a 204 response.  This was incorrect.  The "correct"
  behavior is to do what mod_dav does, which is return a '400
  Bad Request' error.  This was caught by litmus
  locks.notowner_lock test #10.  See
  http://lists.w3.org/Archives/Public/w3c-dist-auth/2001JanMar/0099.html
  for further rationale.

- When Zope properties were set via DAV in the "null" namespace
  (xmlns="") a subsequent PROPFIND for the property would cause the
  XML representation for that property to show a namespace of
  xmlns="None".  Fixed within OFS.PropertySheets.dav__propstat.

- integrated theuni's additional test from 2.11 (see r73132)

- Relaxed requirements for context of
  Products.Five.browser.pagetemplatefile.ZopeTwoPageTemplateFile,
  to reduce barriers for testing renderability of views which
  use them.
  (http://www.zope.org/Collectors/Zope/2327)

- PluginIndexes: Fixed 'parseIndexRequest' for false values.

- Collector #2263: 'field2ulines' did not convert empty string
  correctly.

- Collector #2198: Zope 3.3 fix breaks Five 1.5 test_getNextUtility

- Prevent ZPublisher from insering incorrect <base/> tags into the
  headers of plain html files served from Zope3 resource directories.

- Changed the condition checking for setting status of
  HTTPResponse from to account for new-style classes.

- The Wrapper_compare function from tp_compare to tp_richcompare.
  Also another function Wrapper_richcompare is added.

- The doc test has been slightly changed in ZPublisher to get
  the error message extracted correctly.

- The changes made in Acquisition.c in Implicit Acquisition
  comparison made avail to Explicit Acquisition comparison also.

- zopedoctest no longer breaks if the URL contains more than one
  question mark. It broke even when the second question mark was
  correctly quoted.

Other Changes
+++++++++++++

- Added lib/python/webdav/litmus-results.txt explaining current
  test results from the litmus WebDAV torture test.

- DocumentTemplate.DT_Var.newline_to_br(): Simpler, faster
  implementation.


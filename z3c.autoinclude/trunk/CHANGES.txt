Changes
=======

0.3.5 (unreleased)
------------------

* If a module cannot be resolved, but raises ``ImportError``, log a
  warn and continue. This fixes an issue where the determining the
  includable packages would fail due to a problem with the importation
  of one or potentially more modules. An example is the ``gobject``
  module which provides a Python binding to ``GObject``. In a recent
  API deprecation, one is no longer allowed to both import ``gi`` and
  ``gobject``.

0.3.4 (2011-03-11)
------------------

* Remove unnecessary distribution lookup in the PluginFinder.

0.3.3 (2010-05-06)
------------------

* Ignore case in tests in order to pass tests on Windows.

* Clearly specify license as ZPL (not public domain, as it was
  claiming before).

0.3.2 (2009-12-19)
------------------

* Let `subpackageDottedNames` always return a sorted list of package names as
  `os.listdir` doesn't on some platforms.

0.3.1 (2009-05-04)
------------------

* z3c.autoinclude no longer (spuriously) depends on PasteScript.

0.3 (2009-03-03)
----------------

* Allow virtual namespace packages like 'plone' to be specified for the
  package. I think this may need more thought for the dependency case.

* Allow ZCML ``includePlugins`` directive to specify a particular ZCML file to
  try to load from plugins, so that loading of meta, configure and overrides
  can be split across three ZCML files if desired. You can specify a file like:
  <includePlugins package="." file="silly.zcml" />.

* Provide a separate ``includePluginsOverrides`` directive to be used when
  loading overrides, and no longer look for 'overrides.zcml' files by default
  with ``includePlugins``.

* Removed the deprecated ``autoinclude`` and ``autoincludeOverrides``
  directives.

* Allow autoinclusion to be disabled by setting
  `os.environ['Z3C_AUTOINCLUDE_PLUGINS_DISABLED']` and
  `os.environ['Z3C_AUTOINCLUDE_DEPENDENCIES_DISABLED']`, potentially useful for
  test runners or debugging sessions. See
  http://lists.plone.org/pipermail/framework-team/2009-February/002689.html for
  discussion.

0.2.2 (2008-04-22)
------------------

* Gracefully catch KeyErrors in ``namespaceForDottedName``; get_metadata_lines
  will sometimes throw this for certain distribution types, apparently. In
  particular, some systems' version of Python itself will be wrapped in a
  distribution which throws this error, resulting in system-dependent
  unresumable breakage of z3c.autoinclude prior to this fix.

0.2.1 (2008-04-21)
------------------

* Fixed bug which prevented proper inclusion of packages when the base
  package's namespace has been extended by other installed packages.

* Rewrote ``distributionForPackage`` function.

* Added additional tests for ``includePlugins`` and utility functions.

* Fixed bug which made z3c.autoinclude look for ZCML in namespaces of nested
  namespace packages (eg, if there happened to -- improperly -- be an
  x/y/configure.zcml in a x.y.z package with an x.y namespace, it would have
  been included; this is incorrect.)

0.2 (2008-04-18)
----------------

* Added new directive ``includePlugins``.

* Renamed ``autoinclude`` directive to ``includeDependencies``.

* Deprecated ``autoinclude`` directive.

0.1 (2008-02-25)
----------------

* Initial public release.

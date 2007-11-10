==================
Zope Release Tools
==================

This package provides a set of scripts and tools to manage Good-Known-Sets, or
short KGSs. A KGS is a set of package distributions that are known to work
well together. You can verify this, for example, by running all the tests of
all the packages at once.

Let me show you how a typical controlled packages configuration file looks
like:

  >>> import tempfile
  >>> cfgFile = tempfile.mktemp('-cp.cfg')
  >>> open(cfgFile, 'w').write('''\
  ... [DEFAULT]
  ... tested = true
  ...
  ... [KGS]
  ... name = zope-dev
  ...
  ... [packageA]
  ... versions = 1.0.0
  ...            1.0.1
  ...
  ... [packageB]
  ... versions = 1.2.3
  ...
  ... [packageC]
  ... # Do not test this package.
  ... tested = false
  ... versions = 4.3.1
  ... ''')

As you can see, this file uses an INI-style format. The "DEFAULT" section is
special, as it will insert the specified options into all other sections as
default. The "KGS" section specifies some global information about the KGS,
such as the name of the KGS.

All other sections refer to package names. Currently each package section
supports two options. The "versions" option lists all versions that are known
to work in the KGS. Those versions should *always* only be bug fixes to the
first listed version. The second option, "tested", specifies whether the
package should be part of the KGS test suite. By default, we want all packages
to be tested, but some packages require very specific test setups that cannot
be easily reproduced _[1], so we turn off those tests.

Generating the configuration file and managing it is actually the hard
part. Let's now see what we can do with it.

.. [1]: This is usually due to bugs in setuptools or buildout, such as PYC
files not containing the correct reference to their PY file.


Generate Versions
-----------------

One of the easiest scripts, is the version generation. This script will
generate a "versions" section that is compatible with buildout.

  >>> versionsFile = tempfile.mktemp('-versions.cfg')

  >>> from zope.release import version
  >>> version.main((cfgFile, versionsFile))

  >>> print open(versionsFile, 'r').read()
  [versions]
  packageA = 1.0.1
  packageB = 1.2.3
  packageC = 4.3.1


Generate Buildout
-----------------

In order to be able to test the KGS, you can also generate a full buildout
file that will create and install a testrunner over all packages for you:

  >>> buildoutFile = tempfile.mktemp('-buildout.cfg')

  >>> from zope.release import buildout
  >>> buildout.main((cfgFile, buildoutFile))

  >>> print open(buildoutFile, 'r').read()
  [buildout]
  parts = test
  versions = versions
  <BLANKLINE>
  [test]
  recipe = zc.recipe.testrunner
  eggs = packageA
      packageB
  <BLANKLINE>
  [versions]
  packageA = 1.0.1
  packageB = 1.2.3
  packageC = 4.3.1
  <BLANKLINE>


Uploading Files
---------------

Once the generated files are tested and ready for upload, you can use the
upload script to upload the files to the KGS. Since we do not actually want to
upload files, we simply switch into dry-run mode:

  >>> from zope.release import upload
  >>> upload.DRY_RUN = True

  >>> upload.main((
  ...     cfgFile, versionsFile, buildoutFile,
  ...     'download.zope.org:/zope-dev'
  ...     ))
  scp ...-cp.cfg download.zope.org:/zope-dev/...-cp.cfg
  scp ...-versions.cfg download.zope.org:/zope-dev/...-versions.cfg
  scp ...-buildout.cfg download.zope.org:/zope-dev/...-buildout.cfg


Updating the Zope 3 Tree
------------------------

Since we still want to create a Zope 3 source tree release, we need ot be able
to update its externals using the information of the controlled packages
file. Since this script is clearly Zope3-specific, we need a new controlled
packages config file that contains actual packages:

  >>> import tempfile
  >>> zopeCfgFile = tempfile.mktemp('-cp.cfg')
  >>> open(zopeCfgFile, 'w').write('''\
  ... [DEFAULT]
  ... tested = true
  ...
  ... [KGS]
  ... name = zope-dev
  ...
  ... [ZODB3]
  ... versions = 1.0.0
  ...
  ... [ZConfig]
  ... versions = 1.1.0
  ...
  ... [pytz]
  ... versions = 2007g
  ...
  ... [zope.interface]
  ... versions = 1.2.0
  ...
  ... [zope.app.container]
  ... versions = 1.3.0
  ... ''')

We also need to stub the command execution, since we do not have an actual Zope
3 tree checked out:

  >>> cmdOutput = {
  ...     'svn propget svn:externals Zope3/src': '''\
  ... docutils   path/to/docutils
  ... pytz       path/to/pytz
  ... twisted    path/to/twisted
  ... ZConfig    path/to/ZConfig
  ... ZODB       path/to/ZODB''',
  ...     'svn propget svn:externals Zope3/src/zope': '''\
  ... interface  path/to/zope/interface''',
  ...     'svn propget svn:externals Zope3/src/zope/app': '''\
  ... container  path/to/zope/app/container''',
  ... }

  >>> def do(cmd):
  ...     print cmd
  ...     print '-----'
  ...     return cmdOutput.get(cmd, '')

  >>> from zope.release import tree
  >>> tree.do = do

Let's now run the tree update:

  >>> tree.main((zopeCfgFile, 'Zope3'))
  svn propget svn:externals Zope3/src
  -----
  svn propset svn:externals
    "docutils svn://svn.zope.org/repos/main/docutils/tags/0.4.0/
     pytz svn://svn.zope.org/repos/main/pytz/tags/2007g/src/pytz
     twisted svn://svn.twistedmatrix.com/.../twisted-core-2.5.0/twisted
     ZConfig svn://svn.zope.org/repos/main/ZConfig/tags/1.1.0/ZConfig
     ZODB svn://svn.zope.org/repos/main/ZODB/tags/1.0.0/src/ZODB"
    Zope3/src
  -----
  svn propget svn:externals Zope3/src/zope
  -----
  svn propset svn:externals
    "interface svn://svn.zope.org/repos/main/zope.interface/tags/1.2.0/src/zope/interface" Zope3/src/zope
  -----
  svn propget svn:externals Zope3/src/zope/app
  -----
  svn propset svn:externals
    "container svn://svn.zope.org/repos/main/zope.app.container/tags/1.3.0/src/zope/app/container" Zope3/src/zope/app
  -----


Basic Parser API
----------------

The ``kgs.py`` module provides a simple class that parses the KGS
configuration file and provides all data in an object-oriented manner.

  >>> from zope.release import kgs

The class is simply instnatiated using the path to the config file:

  >>> myKGS = kgs.KGS(cfgFile)
  >>> myKGS
  <KGS 'zope-dev'>

The name of the KGS is available via the `name` attribute:

  >>> myKGS.name
  'zope-dev'

The packages are available under `packages`:

  >>> myKGS.packages
  [<Package 'packageA'>, <Package 'packageB'>, <Package 'packageC'>]

Each package is also an object:

  >>> pkgA = myKGS.packages[0]
  >>> pkgA
  <Package 'packageA'>

  >>> pkgA.name
  'packageA'
  >>> pkgA.versions
  ['1.0.0', '1.0.1']
  >>> pkgA.tested
  True

===============
Known Good Sets
===============

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
  ... version = 1.2.0
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

You can also stack controlled package configurations on top of each
other. Base configurations can be specified using the `extends` option:

  >>> import tempfile
  >>> cfgFile2 = tempfile.mktemp('-cp.cfg')
  >>> open(cfgFile2, 'w').write('''\
  ... [DEFAULT]
  ... tested = true
  ...
  ... [KGS]
  ... name = grok-dev
  ... version = 0.1.0
  ... extends = %s
  ...
  ... [packageA]
  ... versions = 1.0.2
  ...
  ... [packageD]
  ... versions = 2.2.3
  ...            2.2.4
  ... ''' %cfgFile)

As you can see, you can completely override another package's version
specification as well.

Generating the configuration file and managing it is actually the hard
part. Let's now see what we can do with it.

.. [1]: This is usually due to bugs in setuptools or buildout, such as PYC
files not containing the correct reference to their PY file.


Generate Versions
-----------------

One of the easiest scripts, is the version generation. This script will
generate a "versions" section that is compatible with buildout.

  >>> versionsFile = tempfile.mktemp('-versions.cfg')

  >>> from zope.kgs import version
  >>> version.main((cfgFile, versionsFile))

  >>> print open(versionsFile, 'r').read()
  [versions]
  packageA = 1.0.1
  packageB = 1.2.3
  packageC = 4.3.1

Let's now ensure that the versions also work for the extended configuration:

  >>> versionsFile2 = tempfile.mktemp('-versions.cfg')

  >>> version.main((cfgFile2, versionsFile2))

  >>> print open(versionsFile2, 'r').read()
  [versions]
  packageA = 1.0.2
  packageB = 1.2.3
  packageC = 4.3.1
  packageD = 2.2.4


Generate Buildout
-----------------

In order to be able to test the KGS, you can also generate a full buildout
file that will create and install a testrunner over all packages for you:

  >>> buildoutFile = tempfile.mktemp('-buildout.cfg')

  >>> from zope.kgs import buildout
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

Let's make sure that the buildout generation also honors the extensions:

  >>> buildoutFile2 = tempfile.mktemp('-buildout.cfg')

  >>> buildout.main((cfgFile2, buildoutFile2))

  >>> print open(buildoutFile2, 'r').read()
  [buildout]
  parts = test
  versions = versions
  <BLANKLINE>
  [test]
  recipe = zc.recipe.testrunner
  eggs = packageA
      packageB
      packageD
  <BLANKLINE>
  [versions]
  packageA = 1.0.2
  packageB = 1.2.3
  packageC = 4.3.1
  packageD = 2.2.4
  <BLANKLINE>


Flat Links Pages
----------------

We can also create a flat links page that can be used in the
`dependency_links` argument in your `setup.py` file. Since this module
accesses the original PyPI to ask for the download locations and filenames, we
have to create a controlled packages configuration file that contains real
packages with real version numbers:

  >>> cfgFileReal = tempfile.mktemp('-cp.cfg')
  >>> open(cfgFileReal, 'w').write('''\
  ... [DEFAULT]
  ... tested = true
  ...
  ... [KGS]
  ... name = zope-dev
  ... version = 3.4.0b2
  ...
  ... [PIL]
  ... versions = 1.1.6
  ...
  ... [zope.component]
  ... versions = 3.4.0
  ...
  ... [zope.interface]
  ... versions = 3.4.0
  ...            3.4.1
  ...
  ... [z3c.formdemo]
  ... versions = 1.1.0
  ... ''')

Let's now create the links page:

  >>> linksFile = tempfile.mktemp('-links.html')

  >>> from zope.kgs import link
  >>> link.main((cfgFileReal, linksFile))

  >>> print open(linksFile, 'r').read()
  <html>
  <head>
  <title>Links for the "zope-dev" KGS (version 3.4.0b2)</title>
  </head>
  <body>
  <h1>Links for the "zope-dev" KGS (version 3.4.0b2)</h1>
    <a href="http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.1.0-py2.4.egg#md5=9d605bd559ea33ac57ce11f5c80fa3d3">z3c.formdemo-1.1.0-py2.4.egg</a><br/>
    <a href="http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.1.0.tar.gz#md5=f224a49cea737112284f74b859e3eed0">z3c.formdemo-1.1.0.tar.gz</a><br/>
  <a href="http://pypi.python.org/packages/2.4/z/zope.component/zope.component-3.4.0-py2.4.egg#md5=c0763e94912e4a8ac1e321a068c916ba">zope.component-3.4.0-py2.4.egg</a><br/>
  <a href="http://pypi.python.org/packages/source/z/zope.component/zope.component-3.4.0.tar.gz#md5=94afb57dfe605d7235ff562d1eaa3bed">zope.component-3.4.0.tar.gz</a><br/>
  <a href="http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.4.0.tar.gz#md5=0be9fd80b7bb6bee520e56eba7d29c90">zope.interface-3.4.0.tar.gz</a><br/>
  <a href="http://pypi.python.org/packages/2.4/z/zope.interface/zope.interface-3.4.0-py2.4-win32.egg#md5=3fa5e992271375eac597622d8e2fd5ec">zope.interface-3.4.0-py2.4-win32.egg</a><br/>
  <a href="http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.4.1.tar.gz#md5=b085f4a774adab688e037ad32fbbf08e">zope.interface-3.4.1.tar.gz</a><br/>
  </body>
  </html>


PPIX Support
------------

You can also use the KGS to limit the available packages in a package index
generated ``zc.mirrorcheeseshopslashsimple``. This script also uses PyPI to
look up distribution file, so wave to use the real configuration file again.

Let's create the pages:

  >>> indexDir = tempfile.mkdtemp('-ppix')

  >>> from zope.kgs import ppix
  >>> ppix.main((cfgFileReal, indexDir))

The index contains one directory per package. So let's have a look:

  >>> import os
  >>> sorted(os.listdir(indexDir))
  ['PIL', 'z3c.formdemo', 'zope.component', 'zope.interface']

Each directory contains a single "index.html" file with the download links:

  >>> pkgDir = os.path.join(indexDir, 'zope.component')
  >>> sorted(os.listdir(pkgDir))
  ['index.html']

  >>> pkgIndex = os.path.join(pkgDir, 'index.html')
  >>> print open(pkgIndex, 'r').read()
  <html>
  <head>
  <title>Links for "zope.component"</title>
  </head>
  <body>
  <h1>Links for "zope.component"</h1>
  <a href="http://pypi.python.org/packages/2.4/z/zope.component/zope.component-3.4.0-py2.4.egg#md5=c0763e94912e4a8ac1e321a068c916ba">zope.component-3.4.0-py2.4.egg</a><br/>
  <a href="http://pypi.python.org/packages/source/z/zope.component/zope.component-3.4.0.tar.gz#md5=94afb57dfe605d7235ff562d1eaa3bed">zope.component-3.4.0.tar.gz</a><br/>
  </body>
  </html>

PIL is an interesting case, because it does not upload its distribution files
yet, at least not for version 1.1.6:

  >>> pkgIndex = os.path.join(indexDir, 'PIL', 'index.html')
  >>> print open(pkgIndex, 'r').read()
  <html><head><title>Links for PIL</title></head><body><h1>Links for PIL</h1><a href='http://www.pythonware.com/products/pil' rel="homepage">1.1.5 home_page</a><br/>
  <a href='http://effbot.org/zone/pil-changes-115.htm' rel="download">1.1.5 download_url</a><br/>
  <a href='http://www.pythonware.com/products/pil' rel="homepage">1.1.5a2 home_page</a><br/>
  <a href='http://effbot.org/zone/pil-changes-115.htm' rel="download">1.1.5a2 download_url</a><br/>
  <a href='http://www.pythonware.com/products/pil' rel="homepage">1.1.5a1 home_page</a><br/>
  <a href='http://effbot.org/zone/pil-changes-115.htm' rel="download">1.1.5a1 download_url</a><br/>
  <a href='http://www.pythonware.com/products/pil/' rel="homepage">1.1.4 home_page</a><br/>
  <a href='http://www.pythonware.com/products/pil/' rel="homepage">1.1.3 home_page</a><br/>
  <a href='http://www.pythonware.com/downloads/Imaging-1.1.3.tar.gz' rel="download">1.1.3 download_url</a><br/>
  <a href='http://www.pythonware.com/products/pil' rel="homepage">1.1.6 home_page</a><br/>
  <a href='http://effbot.org/downloads/#Imaging' rel="download">1.1.6 download_url</a><br/>
  </body></html>

Optionally, you can also specify the `-i` option to generate an overview:

  >>> ppix.main(('-i', cfgFileReal, indexDir))

  >>> sorted(os.listdir(indexDir))
  ['PIL', 'index.html', 'z3c.formdemo', 'zope.component', 'zope.interface']

Let's now look at the file:

  >>> indexPage = os.path.join(indexDir, 'index.html')
  >>> print open(indexPage, 'r').read()
  <html>
  <head>
  <title>Simple Index for the "zope-dev" KGS (version 3.4.0b2)</title>
  </head>
  <body>
  <h1>Simple Index for the "zope-dev" KGS (version 3.4.0b2)</h1>
  <a href="PIL">PIL</a><br/>
  <a href="z3c.formdemo">z3c.formdemo</a><br/>
  <a href="zope.component">zope.component</a><br/>
  <a href="zope.interface">zope.interface</a><br/>
  </body>
  </html>

Allowing exisitng package pages to be overwritten and making the main index
page an optional feature makes it possible to use this script for two use
cases: (1) Merge the constraints into a PPIX index created by
``zc.mirrorcheeseshopslashsimple``, and (2) create a standalone index which
only provides the packages of the KGS.


Getting the Latest Versions
---------------------------

When updating the KGS, it is often useful to know for which packages have new
releases.

  >>> from zope.kgs import latest
  >>> latest.main((cfgFileReal,))
  z3c.formdemo: 1.1.1, 1.1.2, 1.2.0, 1.3.0, 1.3.0b1, 1.4.0, ...

However, it is often desired only to show new minor versions; in this case, we
can pass an option to exclude all versions that have a different major
version:

  >>> latest.main(('-m', cfgFileReal))
  z3c.formdemo: 1.1.1, 1.1.2

Sometimes you're only interested in changes that apply to a single package,
and you won't want to wait for the script to query all of the others

  >>> latest.main(('-m', cfgFileReal, 'zope.app.server'))

  >>> latest.main(('-m', cfgFileReal, 'z3c.formdemo'))
  z3c.formdemo: 1.1.1, 1.1.2


Extracting Change Information
-----------------------------

When releasing a version of the KGS, it is desirable to produce a list of
changes since the last release. Changes are commonly compared to an older
version.

  >>> cfgFileRealOrig = tempfile.mktemp('-cp.cfg')
  >>> open(cfgFileRealOrig, 'w').write('''\
  ... [DEFAULT]
  ... tested = true
  ...
  ... [KGS]
  ... name = zope-dev
  ... version = 3.4.0b1
  ...
  ... [PIL]
  ... versions = 1.1.6
  ...
  ... [zope.component]
  ... versions = 3.4.0
  ...
  ... [zope.interface]
  ... versions = 3.4.0
  ... ''')

Let's now produce the changes:

  >>> from zope.kgs import change
  >>> change.main((cfgFileReal, cfgFileRealOrig))
  ===                                                                               
  PIL                                                                               
  ===                                                                               
  <BLANKLINE>                                                                       
  <BLANKLINE>                                                                       
  ============                                                                      
  z3c.formdemo                                                                      
  ============                                                                      
  <BLANKLINE>                                                                       
  1.1.0 (None)                                                                      
  ------------                                                                      
  <BLANKLINE>                                                                       
  - Feature: New "SQL Message" demo shows how ``z3c.form`` can be used with         
    non-object data. Specificically, this small application demonstrates using a    
    Gadfly database using pure SQL calls without any ORM.                           
  <BLANKLINE>                                                                       
  - Feature: New "Address Book" demo that demonstrates more complex use cases,      
    such as subforms, composite widgets, and mappings/lists
  <BLANKLINE>
  <BLANKLINE>
  ==============
  zope.component
  ==============
  <BLANKLINE>
  3.4.0 (2007-09-29)
  ------------------
  <BLANKLINE>
  No further changes since 3.4.0a1.
  <BLANKLINE>
  <BLANKLINE>
  ==============
  zope.interface
  ==============
  <BLANKLINE>
  3.4.1 (None)
  ------------
  <BLANKLINE>
  Fixed a setup bug that prevented installation from source on systems
  without setuptools.
  <BLANKLINE>
  3.4.0 (None)
  ------------
  <BLANKLINE>
  Final release for 3.4.0.
  <BLANKLINE>
  <BLANKLINE>


You can also create the changes without an original file, in which case only
the versions listed in the current KGS are considered.

  >>> change.main((cfgFileReal,))
  ===                                                                               
  PIL                                                                               
  ===                                                                               
  <BLANKLINE>                                                                       
  <BLANKLINE>                                                                       
  ============                                                                      
  z3c.formdemo                                                                      
  ============                                                                      
  <BLANKLINE>                                                                       
  1.1.0 (None)                                                                      
  ------------                                                                      
  <BLANKLINE>                                                                       
  - Feature: New "SQL Message" demo shows how ``z3c.form`` can be used with         
    non-object data. Specificically, this small application demonstrates using a    
    Gadfly database using pure SQL calls without any ORM.                           
  <BLANKLINE>                                                                       
  - Feature: New "Address Book" demo that demonstrates more complex use cases,      
    such as subforms, composite widgets, and mappings/lists
  <BLANKLINE>
  <BLANKLINE>
  ==============
  zope.component
  ==============
  <BLANKLINE>
  3.4.0 (2007-09-29)
  ------------------
  <BLANKLINE>
  No further changes since 3.4.0a1.
  <BLANKLINE>
  <BLANKLINE>
  ==============
  zope.interface
  ==============
  <BLANKLINE>
  3.4.1 (None)
  ------------
  <BLANKLINE>
  Fixed a setup bug that prevented installation from source on systems
  without setuptools.
  <BLANKLINE>
  3.4.0 (None)
  ------------
  <BLANKLINE>
  Final release for 3.4.0.
  <BLANKLINE>
  <BLANKLINE>

Introduction Page
-----------------

Once all the files have been created, one can generate an introduction page
that explains how the files can be used. It also lists all the files by
distribution. In order for this script to work, you need the following
directory layout:

  >>> kgsDir = tempfile.mkdtemp()

  >>> open(os.path.join(kgsDir, 'controlled-packages.cfg'), 'w').write(' ')
  >>> open(os.path.join(kgsDir, 'buildout.cfg'), 'w').write(' ')
  >>> open(os.path.join(kgsDir, 'versions.cfg'), 'w').write(' ')
  >>> open(os.path.join(kgsDir, 'links.html'), 'w').write(' ')
  >>> os.mkdir(os.path.join(kgsDir, 'minimal'))

  >>> open(os.path.join(kgsDir, 'controlled-packages-1.0.0.cfg'), 'w').write(' ')
  >>> open(os.path.join(kgsDir, 'buildout-1.0.0.cfg'), 'w').write(' ')
  >>> open(os.path.join(kgsDir, 'versions-1.0.0.cfg'), 'w').write(' ')
  >>> os.mkdir(os.path.join(kgsDir, 'minimal-1.0.0'))

  >>> open(os.path.join(kgsDir, 'controlled-packages-1.1.0.cfg'), 'w').write(' ')
  >>> open(os.path.join(kgsDir, 'buildout-1.1.0.cfg'), 'w').write(' ')
  >>> open(os.path.join(kgsDir, 'versions-1.1.0.cfg'), 'w').write(' ')
  >>> open(os.path.join(kgsDir, 'links-1.1.0.html'), 'w').write(' ')
  >>> os.mkdir(os.path.join(kgsDir, 'minimal-1.1.0'))

  >>> open(os.path.join(kgsDir, 'index.html'), 'w').write(' ')

Let's now generate the page:

  >>> introPage = os.path.join(kgsDir, 'intro.html')

  >>> from zope.kgs import intro
  >>> intro.main((introPage,))

  >>> print open(introPage, 'r').read()
    <!DOCTYPE ...
      <body>
        <h1>Introduction to the KGS</h1>
        <h2>Available Versions</h2>
        <h3>Version 1.0.0</h3>
        <ul>
          <li>
            <a href="controlled-packages-1.0.0.cfg">Controlled Packages</a>
          </li>
          <li>
            <a href="buildout-1.0.0.cfg">Buildout Configuration</a>
          </li>
          <li>
            <a href="versions-1.0.0.cfg">Versions</a>
          </li>
          <li>
            <a href="minimal-1.0.0">Minimal Index</a>
          </li>
          <li>
            <a href="index.html">Index</a>
          </li>
        </ul>
        <h3>Version 1.1.0</h3>
        <ul>
          <li>
            <a href="controlled-packages-1.1.0.cfg">Controlled Packages</a>
          </li>
          <li>
            <a href="buildout-1.1.0.cfg">Buildout Configuration</a>
          </li>
          <li>
            <a href="versions-1.1.0.cfg">Versions</a>
          </li>
          <li>
            <a href="links-1.1.0.html">Package Links</a>
          </li>
          <li>
            <a href="minimal-1.1.0">Minimal Index</a>
          </li>
          <li>
            <a href="index.html">Index</a>
          </li>
        </ul>
        ...
      </body>
    </html>


The Site Generator
------------------

The easiest way to publish the KGS is via a directory published by a Web
server. Whenever a new `controlled-packages.cfg` file is uploaded, a script is
run that generates all the files. I usually set up a crontab job to do
this. The site generator script acts upon a directory, in which it assumes a
`controlled-packages.cfg` file was placed:

  >>> siteDir = tempfile.mkdtemp()
  >>> cfgFileSite = os.path.join(siteDir, 'controlled-packages.cfg')

  >>> import shutil
  >>> shutil.copy(cfgFileReal, cfgFileSite)

  >>> from zope.kgs import site
  >>> site.main((siteDir,))

Let's have a look at the generated files:

  >>> sorted(os.listdir(siteDir))
  ['PIL',
   'buildout-3.4.0b2.cfg', 'buildout.cfg',
   'cf-timestamp',
   'controlled-packages-3.4.0b2.cfg', 'controlled-packages.cfg',
   'intro.html',
   'links-3.4.0b2.html', 'links.html',
   'minimal', 'minimal-3.4.0b2',
   'versions-3.4.0b2.cfg', 'versions.cfg',
   'z3c.formdemo', 'zope.component', 'zope.interface']

  >>> sorted(os.listdir(os.path.join(siteDir, 'minimal')))
  ['PIL', 'index.html', 'z3c.formdemo', 'zope.component', 'zope.interface']

If you try to generate the site again without changing the controlled packages
config file, it will simply return, because it checks the timestamp from the
previous generation:

  >>> tsPath = os.path.join(siteDir, 'cf-timestamp')

  >>> beforeTimestamp = open(tsPath).read()
  >>> site.main((siteDir,))
  >>> afterTimestamp = open(tsPath).read()

  >>> beforeTimestamp == afterTimestamp
  True


Basic Parser API
----------------

The ``kgs.py`` module provides a simple class that parses the KGS
configuration file and provides all data in an object-oriented manner.

  >>> from zope.kgs import kgs

The class is simply instnatiated using the path to the config file:

  >>> myKGS = kgs.KGS(cfgFile)
  >>> myKGS
  <KGS 'zope-dev'>

The name and version  of the KGS is available via:

  >>> myKGS.name
  'zope-dev'
  >>> myKGS.version
  '1.2.0'

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

As we have seen in the scripts above, the KGS class also supports the
`entends` option. Thus, let's load the KGS for the config file 2:

  >>> myKGS2 = kgs.KGS(cfgFile2)
  >>> myKGS2
  <KGS 'grok-dev'>

  >>> myKGS2.name
  'grok-dev'

  >>> myKGS2.packages
  [<Package 'packageA'>,
   <Package 'packageB'>,
   <Package 'packageC'>,
   <Package 'packageD'>]

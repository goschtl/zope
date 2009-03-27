=========================
Zope-Related Web Features
=========================

This page contains features that are specific to Zope projects.


Zope Project Feature
--------------------

The Zope project feature converts a project from a simple Buildout project to
a full Zope server installation.

  >>> from z3c.feature.zope import project
  >>> zprj = project.ZopeProjectFeature()
  >>> zprj
  <ZopeProjectFeature u'Zope Project'>

Clearly, the Zope Project Feature implements its own interface:

  >>> from zope.interface.verify import verifyObject
  >>> from z3c.feature.zope import interfaces

  >>> verifyObject(interfaces.IZopeProjectFeature, zprj)
  True

Each feature must provide a title and some documentation:

  >>> print zprj.featureTitle
  Zope Project

  >>> print zprj.featureDocumentation
  This feature extends a buildout project to a Zope project.

Let's now create a project to which we can apply the feature.

  >>> from z3c.builder.core.project import BuildoutProjectBuilder
  >>> demo = BuildoutProjectBuilder(u'demo')

  >>> zprj.applyTo(demo)

The easiest way to see what the feature added is by rendering the project
itself.

  >>> demo.update()
  >>> demo.write(buildPath)

  >>> ls(buildPath)
  demo/
    bootstrap.py
    buildout.cfg
    setup.py
    src/
      demo/
        __init__.py
        application.zcml
        configure.zcml
        browser/
          __init__.py
          configure.zcml

You immediately notice that there are several files:

- `browser/` - This is a placeholder sub-package for all browser-related
  code. It contains a placeholder configuration file.

    >>> more(buildPath, 'demo', 'src', 'demo', 'browser', 'configure.zcml')
    <configure
        i18n_domain="demo"
        />

- `application.zcml` - This file contains all the necessary includes
  to make the Zope 3 application run.

    >>> more(buildPath, 'demo', 'src', 'demo', 'application.zcml')
    <configure
        xmlns:zope="http://namespaces.zope.org/zope"
        xmlns:browser="http://namespaces.zope.org/browser"
        i18n_domain="demo"
        >
      <zope:include
          package="zope.app.component"
          file="meta.zcml"
          />
      ...
      <browser:menu
          title="Views"
          id="zmi_views"
          />
      <browser:menu
          title="Actions"
          id="zmi_actions"
          />
      <zope:include
          package="zope.app.appsetup"
          />
      ...
      <browser:defaultView
          name="index.html"
          />
      <zope:securityPolicy
          component="zope.securitypolicy.zopepolicy.ZopeSecurityPolicy"
          />
      <zope:role
          title="Everybody"
          id="zope.Anonymous"
          />
      <zope:grantAll
          role="zope.Anonymous"
          />
    </configure>

- `configure.zcml` - This is a simple placeholder configuration file for
  future use.

    >>> more(buildPath, 'demo', 'src', 'demo', 'configure.zcml')
    <configure
        xmlns:zope="http://namespaces.zope.org/zope"
        i18n_domain="demo"
        >
      <zope:include
          package=".browser"
          />
    </configure>

Clearly with so many references to other packages, the setup file must also
list dependencies.

  >>> more(buildPath, 'demo', 'setup.py')
  ##############################################################################
  #
  # This file is part of demo...
  #
  ##############################################################################
  """Setup"""
  from setuptools import setup, find_packages
  <BLANKLINE>
  setup (
      name = 'demo',
      version = '0.1.0',
      author = u"",
      author_email = u"",
      description = u"",
      license = "GPLv3",
      keywords = u"",
      url = "http://pypi.python.org/pypi/demo",
      classifiers = [],
      packages = find_packages('src'),
      include_package_data = True,
      package_dir = {'':'src'},
      namespace_packages = [],
      extras_require = {},
      install_requires = [
          'setuptools',
          'zdaemon',
          ...
          ],
      zip_safe = False,
      entry_points = {},
      )

Also, the buildout configuration file contain multiple new sections that setup
the application server

  >>> more(buildPath, 'demo', 'buildout.cfg')
  [buildout]
  extends = http://download.zope.org/zope3.4/3.4.0/versions.cfg
  develop = .
  parts = demo-app demo
  versions = versions
  <BLANKLINE>
  [zope3]
  location = .
  <BLANKLINE>
  [demo-app]
  recipe = zc.zope3recipes:app
  site.zcml = <include package="demo" file="application.zcml" />
  eggs = demo
  <BLANKLINE>
  [demo]
  recipe = zc.zope3recipes:instance
  application = demo-app
  zope.conf = ${database:zconfig}
  eggs = demo
  <BLANKLINE>
  [database]
  recipe = zc.recipe.filestorage


Zope Browser Layer Feature
--------------------------

Not yet done.


Zope Page Feature
-----------------

This feature installs a simple page. It provides a few options that alter the
outcome of the generation.

  >>> from z3c.feature.zope import browser
  >>> page = browser.ZopePageFeature()
  >>> page
  <ZopePageFeature u'Zope Page (index.html)'>

Clearly, the feature implements its own interface:

  >>> verifyObject(interfaces.IZopePageFeature, page)
  True

Each feature must provide a title and some documentation:

  >>> print page.featureTitle
  Zope Page (index.html)

  >>> print page.featureDocumentation
  The Zope Page Feature creates a simple Zope 3 style page.

This particular feature has some additional fields that can be customized.

  >>> print page.name
  index.html
  >>> print page.templateName
  None

If we change the page name, the feature title changes as well.

  >>> page.name = u"page.html"
  >>> print page.featureTitle
  Zope Page (page.html)

Now that we have the page setup, let's apply it to the project and render the
project again.

  >>> page.update()
  >>> page.applyTo(demo)

  >>> demo.update()
  >>> demo.write(buildPath, True)

  >>> ls(buildPath)
  demo/
    bootstrap.py
    buildout.cfg
    setup.py
    src/
      demo/
        __init__.py
        application.zcml
        configure.zcml
        browser/
          __init__.py
          configure.zcml
          page.pt

The page template is the simplest HTML page possible:

  >>> more(buildPath, 'demo', 'src', 'demo', 'browser', 'page.pt')
  <html>
    <head>
      <title>Simple Page</title>
    </head>
    <body>
      <h1>Simple Page</h1>
    </body>
  </html>

The configuration file also registers the page:

  >>> more(buildPath, 'demo', 'src', 'demo', 'browser', 'configure.zcml')
  <configure
      xmlns:browser="http://namespaces.zope.org/browser"
      i18n_domain="demo"
      >
    <browser:page
        template="page.pt"
        for="*"
        name="page.html"
        permission="zope.Public"
        />
  </configure>

Pretty simple.

Bulding the Project
-------------------

Before we can build the project, we need to install the Python interpreter
feature and re-render the project.

  >>> from z3c.feature.core import python
  >>> interpreter = python.PythonInterpreterFeature()
  >>> interpreter.applyTo(demo)

  >>> demo.update()
  >>> demo.write(buildPath, True)

Let's now build the project to see whether it all works.

  >>> import sys
  >>> projectDir = buildPath + '/demo'

  >>> print cmd((sys.executable, 'bootstrap.py'), projectDir)
  Exit Status: 0...
  Downloading http://pypi.python.org/packages/2.5/s/setuptools/setuptools-...
  Creating directory '.../demo/bin'.
  Creating directory '.../demo/parts'.
  Creating directory '.../demo/develop-eggs'.
  Generated script '.../demo/bin/buildout'.

  >>> print cmd(('./bin/buildout', '-N'), projectDir)
  Exit Status: 0
  Develop: '.../demo/.'
  Installing demo-app.
  Generated script '.../demo/parts/demo-app/runzope'.
  Generated script '.../demo/parts/demo-app/debugzope'.
  Installing database.
  Installing demo.
  Generated script '.../demo/bin/demo'.
  Installing python.
  Generated interpreter '.../demo/bin/python'.

Let's now load the configuration to check that we have a fully functioning
package.

  >>> testCode = '''
  ... import zope.app.twisted.main
  ... from zc.zope3recipes import debugzope
  ... options = debugzope.load_options(
  ...     ('-C', '%(dir)s/parts/demo/zope.conf',),
  ...     zope.app.twisted.main)
  ... folder = debugzope.zglobals(options.configroot)['root']
  ...
  ... import zope.component
  ... from zope.publisher.browser import TestRequest
  ... page = zope.component.getMultiAdapter(
  ...     (folder, TestRequest()), name='page.html')
  ... print page()
  ... ''' % {'dir': projectDir}

  >>> print cmd(('./bin/python', '-c', testCode), projectDir)
  Exit Status: 0
  <html>
    <head>
      <title>Simple Page</title>
    </head>
    <body>
      <h1>Simple Page</h1>
    </body>
  </html>

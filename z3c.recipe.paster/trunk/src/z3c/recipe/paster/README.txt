=======================
z3c.recipe.paster:serve
=======================

This Zope 3 recipes offers a Paste Deploy setup for Zope3 projects. It requires
to define a Paste Deploy *.ini file in the buoldout.cfg. If you need a simple
PasteScript setup you can use the z3c.recipe.paster:paster recipe which allows
to run already existing ``*.ini`` files.


Options
-------

The 'serve' recipe accepts the following options:

eggs
  The names of one or more eggs, with their dependencies that should
  be included in the Python path of the generated scripts.

ini
  The paste deploy ``*.ini`` file content.

zope.conf
  The zope.conf file defining the DB used in the WSGI app and the error log
  section.

site.zcml
  The zope site.zcml file used by the zope application.


Test
----

Lets define a (bogus) eggs that we can use in our application:

  >>> mkdir('demo')
  >>> write('demo', 'setup.py',
  ... '''
  ... from setuptools import setup
  ... setup(name = 'demo')
  ... ''')

Now check if the setup was correct:

  >>> ls('bin')
  -  buildout

We'll create a ``buildout.cfg`` file that defines our paster serve configuration:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... develop = demo
  ... parts = var myapp
  ...
  ... [var]
  ... recipe = zc.recipe.filestorage
  ...
  ... [myapp]
  ... eggs = demo
  ... recipe = z3c.recipe.paster:serve
  ... ini =
  ...   [app:main]
  ...   use = egg:demo
  ...
  ...   [server:main]
  ...   use = egg:Paste#http
  ...   host = 127.0.0.1
  ...   port = 8080
  ...
  ... zope.conf =
  ...
  ...   ${var:zconfig}
  ...
  ...   <eventlog>
  ...     <logfile>
  ...       formatter zope.exceptions.log.Formatter
  ...       path ${buildout:directory}/parts/myapp/error.log
  ...     </logfile>
  ...     <logfile>
  ...       formatter zope.exceptions.log.Formatter
  ...       path STDOUT
  ...     </logfile>
  ...   </eventlog>
  ...
  ...  devmode on
  ...
  ... site.zcml =
  ...   <!-- inlcude other zcml files like principals.zcml or securitypolicy.zcml
  ...        and your app configuration -->
  ...   <include package="demo" file="app.zcml" />
  ...
  ... ''' % globals())

Now, Let's run the buildout and see what we get:

  >>> print system(join('bin', 'buildout')),
  Develop: '/sample-buildout/demo'
  Installing var.
  Installing myapp.
  Generated script '/sample-buildout/bin/myapp'.

The bin folder contains the scripts for serve our new created paste deploy
server:

  >>> ls('bin')
  -  buildout
  -  myapp

Check the content of our new generated myapp script. As you can see, the
generated script uses the ``paste.script.command.run`` for starting our server:

  >>> cat('bin', 'myapp')
  #!"C:\Python24\python.exe"
  <BLANKLINE>
  import sys
  sys.path[0:0] = [
    '/sample-buildout/demo',
    '/sample-pyN.N.egg',
    ...
    '/sample-pyN.N.egg',
    ]
  <BLANKLINE>
  import os
  sys.argv[0] = os.path.abspath(sys.argv[0])
  <BLANKLINE>
  <BLANKLINE>
  import paste.script.command
  <BLANKLINE>
  if __name__ == '__main__':
      sys.exit(paste.script.command.run([
    'serve', '/sample-buildout/parts/myapp/myapp.ini',
    ]+sys.argv[1:]))

Those ``sample-pyN.N.egg`` lines should be PasteScript and it's dependencies.

Check the content of our new generated myapp.ini file:

  >>> cat('parts', 'myapp', 'myapp.ini')
  <BLANKLINE>
  [app:main]
  use = egg:demo
  [server:main]
  use = egg:Paste#http
  host = 127.0.0.1
  port = 8080


Entry point
-----------

As you probably know, there is some magic going on during startup. The section
``app:main`` in the myapp.ini file above must be defined as entry_point in your
projects setup.py file. Without them, the ``app:main`` isn't available. You can
define such a app:main entry point using the default ``application_factory``
offered from the ``z3c.recipe.paster.wsgi`` package. Of corse you can define
your own application factory if you need to pass some additional configuration
for your app to the factroy defined in your custom ``*.ini`` file.

The default entry_point offered from the z3c.recipe.paster could be included in
your custom setup.py file like::

  setup(
      name = 'something',
      version = '0.5.0dev',
      ...
      include_package_data = True,
      package_dir = {'':'src'},
      namespace_packages = [],
      install_requires = [
          'some.package',
          ],
      entry_points = """
          [paste.app_factory]
          main = z3c.recipe.paster.wsgi:application_factory
          """,
  )

=====================
Z3 development recipe
=====================

z3c.recipe.dev app
------------------

This Zope 3 recipes allows you to define Zope applications.

The 'app' recipe can be used to define a Zope application. It is designed to
work with with Zope solely from eggs. The app recipe causes a part to be
created. The part will contain the application's `zope.conf`, `site.zcml`,
`principals.zcml` and `securitypolicy.zcml`. This configuration files will get
recreated during each update. Another folder called logs will get created and
contains the `access.log` and `z3c.log` files. This log files doesn't get
recreated. The start script itself is located in the bin folder and uses the
configuration files from the relevant parts folder.


Options
*******

The 'app' recipe accepts the following options:

eggs
  The names of one or more eggs, with their dependencies that should
  be included in the Python path of the generated scripts.

server
  The ``zserver`` or ``twisted`` server otpion.

zope.conf
  The contents of zope.conf.

site.zcml
  The contents of site.zcml.

principals.zcml
  The contents of securitypolicy.zcml.

securitypolicy.zcml
  The contents of securitypolicy.zcml.

site.zcml
  The contents of site.zcml.


Test
****

Lets define some (bogus) eggs that we can use in our application:

  >>> mkdir('demo1')
  >>> write('demo1', 'setup.py',
  ... '''
  ... from setuptools import setup
  ... setup(name = 'demo1')
  ... ''')

  >>> mkdir('demo2')
  >>> write('demo2', 'setup.py',
  ... '''
  ... from setuptools import setup
  ... setup(name = 'demo2', install_requires='demo1')
  ... ''')

We'll create a `buildout.cfg` file that defines our application:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... develop = demo1 demo2
  ... parts = myapp var
  ...
  ... [myapp]
  ... recipe = z3c.recipe.dev:app
  ... eggs = demo2
  ...        z3c.recipe.dev [test]
  ... server = zserver
  ... zope.conf = ${var:zconfig}
  ...   <eventlog>
  ...     #level DEBUG
  ...     <logfile>
  ...       path STDOUT
  ...       formatter zope.exceptions.log.Formatter
  ...     </logfile>
  ...   </eventlog>
  ...
  ...   devmode on
  ...
  ... site.zcml =
  ...     <include package="demo1" />
  ...     <include package="demo2" />
  ...
  ... principals.zcml =
  ...   <unauthenticatedPrincipal
  ...       id="lovelybooks.anybody"
  ...       title="Unauthenticated User"
  ...       />
  ...
  ...   <unauthenticatedGroup
  ...       id="zope.Anybody"
  ...       title="Unauthenticated Users"
  ...       />
  ...
  ...   <authenticatedGroup
  ...       id="zope.Authenticated"
  ...       title="Authenticated Users"
  ...       />
  ...
  ...   <everybodyGroup
  ...       id="zope.Everybody"
  ...       title="All Users"
  ...       />
  ...
  ...   <principal
  ...       id="zope.manager"
  ...       title="Manager"
  ...       login="Manager"
  ...       password="password"
  ...       />
  ...
  ...   <grant
  ...       role="zope.Manager"
  ...       principal="zope.manager"
  ...       />
  ...
  ... securitypolicy.zcml =
  ...   <include package="zope.app.securitypolicy" />
  ...
  ...   <securityPolicy
  ...       component="zope.app.securitypolicy.zopepolicy.ZopeSecurityPolicy"
  ...       />
  ...
  ...   <role id="zope.Anonymous" title="Everybody"
  ...       description="All users have this role implicitly" />
  ...   <role id="zope.Manager" title="Site Manager" />
  ...   <role id="zope.Member" title="Site Member" />
  ...
  ...   <!-- Replace the following directive if you don't want public access -->
  ...   <grant permission="zope.View"
  ...        role="zope.Anonymous"
  ...        />
  ...   <grant permission="zope.app.dublincore.view"
  ...        role="zope.Anonymous"
  ...        />
  ...
  ...   <grantAll role="zope.Manager" />
  ...
  ... [var]
  ... recipe = zc.recipe.filestorage
  ...
  ... ''' % globals())

Now, Let's run the buildout and see what we get:

  >>> print system(join('bin', 'buildout')),
  Develop: '/sample-buildout/demo1'
  Develop: '/sample-buildout/demo2'
  Installing var.
  Installing myapp.
  Generated script '/sample-buildout/bin/myapp'.

The bin folder contains the start script:

  >>> ls('bin')
  -  buildout-script.py
  -  buildout.exe
  -  myapp-script.py
  -  myapp.exe

The myapp-scrip.py contains the start code for our zope setup:

  >>> cat('bin', 'myapp-script.py')
  #!"C:\Python24\python.exe"
  <BLANKLINE>
  import sys
  sys.path[0:0] = [
    '/sample-buildout/demo2',
    '/z3c.recipe.dev/trunk/src',
    '/sample-buildout/eggs/zc.recipe.filestorage-1.0.1-py2.4.egg',
    '/sample-buildout/eggs/zope.testing-3.7.1-py2.4.egg',
    '/sample-buildout/eggs/zc.recipe.egg-1.1.0-py2.4.egg',
    '/sample-buildout/eggs/zc.buildout-1.1.1-py2.4.egg',
    '/site-packages',
    '/sample-buildout/eggs/zconfig-2.6.1-py2.4.egg',
    '/sample-buildout/demo1',
    '/sample-buildout/eggs/zope.interface-3.5.0-py2.4-win32.egg',
    ]
  <BLANKLINE>
  import os
  sys.argv[0] = os.path.abspath(sys.argv[0])
  <BLANKLINE>
  <BLANKLINE>
  import zope.app.server.main
  <BLANKLINE>
  if __name__ == '__main__':
      zope.app.server.main.main([
    '-C', '/sample-buildout/parts/myapp/zope.conf',
    ]+sys.argv[1:])

And the myapp folder contains the configure files:

  >>> ls('parts', 'myapp')
  -  principals.zcml
  -  securitypolicy.zcml
  -  site.zcml
  -  zope.conf


z3c.recipe.dev script
---------------------

The script recipe allows us to point to scripts which the recipe will install
a execute script hook for us. You can use this if you need to run a python
script which knows about some egg packages.


Options
*******

The 'script' recipe accepts the following options:

eggs
  The names of one or more eggs, with their dependencies that should
  be included in the Python path of the generated scripts.

module
  The ``module`` which contains the ``method`` to be executed.

method
  The ``method`` which get called from the ``module``.

arguments
  Use the option ``arguments`` to pass arguments to the script.
  All the string will be copied to the script 1:1.
  So what you enter here is what you get.


Test
****

Lets define a egg that we can use in our application:

  >>> mkdir('hello')
  >>> write('hello', 'setup.py',
  ... '''
  ... from setuptools import setup
  ... setup(name = 'hello')
  ... ''')

And let's define a python module which we use for our test:

  >>> write('hello', 'helloworld.py',
  ... """
  ... def helloWorld(*args):
  ...     print 'Hello World'
  ...     for a in args:
  ...         print a
  ... """)

Alos add a `__init__` to the `hello` package:

  >>> write('hello', '__init__.py', '#make package')

We'll create a `buildout.cfg` file that defines our script:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... develop = hello
  ... parts = helloworld
  ...
  ... [helloworld]
  ... recipe = z3c.recipe.dev:script
  ... eggs = hello
  ... module = hello.helloworld
  ... method = helloWorld
  ...
  ... ''' % globals())

Let's run buildout again:

  >>> print system(join('bin', 'buildout')),
  Develop: '/sample-buildout/hello'
  Uninstalling myapp.
  Uninstalling var.
  Installing helloworld.
  Generated script '/sample-buildout/bin/helloworld'.

And check the script again. Now we see the `helloWorld()` method is used:

  >>> cat('bin', 'helloworld-script.py')
  #!C:\Python24\python.exe
  <BLANKLINE>
  import sys
  sys.path[0:0] = [
    '/sample-buildout/hello',
    ]
  <BLANKLINE>
  import os
  sys.argv[0] = os.path.abspath(sys.argv[0])
  <BLANKLINE>
  <BLANKLINE>
  import hello.helloworld
  <BLANKLINE>
  if __name__ == '__main__':
      hello.helloworld.helloWorld()

Now we can call the script:

  >>> print system(join('bin', 'helloworld')),
  Hello World


Test with parameters
********************

Of the same script defined above.

Use the option `arguments = ` to pass arguments to the script.
All the string will be copied to the script 1:1.
So what you enter here is what you get.

We'll create a `buildout.cfg` file that defines our script:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... develop = hello
  ... parts = helloworld
  ...
  ... [helloworld]
  ... recipe = z3c.recipe.dev:script
  ... eggs = hello
  ... module = hello.helloworld
  ... method = helloWorld
  ... arguments = 'foo', 'bar'
  ...
  ... ''' % globals())

Let's run buildout again:

  >>> print system(join('bin', 'buildout')),
  Develop: '/sample-buildout/hello'
  Uninstalling helloworld.
  Installing helloworld.
  Generated script '/sample-buildout/bin/helloworld'.

And check the script again. Now we see the `helloWorld()` method is used:

  >>> cat('bin', 'helloworld-script.py')
  #!C:\Python24\python.exe
  <BLANKLINE>
  import sys
  sys.path[0:0] = [
    '/sample-buildout/hello',
    ]
  <BLANKLINE>
  import os
  sys.argv[0] = os.path.abspath(sys.argv[0])
  <BLANKLINE>
  <BLANKLINE>
  import hello.helloworld
  <BLANKLINE>
  if __name__ == '__main__':
      hello.helloworld.helloWorld('foo', 'bar')

Now we can call the script:

  >>> print system(join('bin', 'helloworld')),
  Hello World
  foo
  bar

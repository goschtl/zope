=========================
Persistent Python Modules
=========================

Persistent Python modules allow us to develop and store Python modules in the
ZODB in contrast to storing them on the filesystem. You might want to look at
the `zodbcode` package for the details of the implementation. In Zope 3 we
implemented persistent modules as utilities. These utilities are known as
module managers that manage the source code, compiled module and name of the
module. We then provide a special module registry that looks up the utilities
to find modules.


The Module Manager
------------------

One can simply create a new module manager by instantiating it:

  >>> from zope.app.module.manager import ModuleManager
  >>> manager = ModuleManager()

If I create the manager without an argument, there is no source code:

  >>> manager.source
  ''

When we add some code

  >>> manager.source = """\n
  ... foo = 1
  ... def bar(): return foo
  ... class Blah(object):
  ...     def __init__(self, id): self.id = id
  ...     def __repr__(self): return 'Blah(id=%s)' % self.id
  ... """

we can get the compiled module and use the created objects:

  >>> module = manager.getModule()
  >>> module.foo
  1
  >>> module.bar()
  1
  >>> module.Blah('blah')
  Blah(id=blah)

We can also ask for the name of the module:

  >>> manager.name
  >>> module.__name__

But why is it `None`? Because we have no registered it yet. Once we register
and activate the registration a name will be set:

  >>> from zope.app.testing import setup
  >>> root = setup.buildSampleFolderTree()
  >>> root_sm = setup.createSiteManager(root)

  >>> from zope.app.module import interfaces
  >>> manager = setup.addUtility(root_sm, 'mymodule',
  ...                            interfaces.IModuleManager, manager)

  >>> manager.name
  'mymodule'

  >>> manager.getModule().__name__
  'mymodule'

Next, let's ensure that the module's persistence works correctly. To do that
let's create a database and add the root folder to it:

  >>> from ZODB.tests.util import DB
  >>> db = DB()
  >>> conn = db.open()
  >>> conn.root()['Application'] = root

  >>> import transaction
  >>> transaction.commit()

Let's now reopen the database to test that the module can be seen from a
different connection.

  >>> conn2 = db.open()
  >>> root2 = conn2.root()['Application']
  >>> module2 = root2.getSiteManager().queryUtility(
  ...     interfaces.IModuleManager, 'mymodule').getModule()
  >>> module2.foo
  1
  >>> module2.bar()
  1
  >>> module2.Blah('blah')
  Blah(id=blah)


Module Lookup API
-----------------

The way the persistent module framework hooks into Python is via module
registires that behave pretty much like `sys.modules`. Zope 3 provides its own
module registry that uses the registered utilities to look up modules:

  >>> from zope.app.module import ZopeModuleRegistry
  >>> ZopeModuleRegistry.findModule('mymodule')

But why did we not get the module back? Because we have not set the site yet:

  >>> from zope.app.component import hooks
  >>> hooks.setSite(root)

Now it will find the module and we can retrieve a list of all persistent
module names:

  >>> ZopeModuleRegistry.findModule('mymodule') is module
  True
  >>> ZopeModuleRegistry.modules()
  ['mymodule']

Additionally, the package provides two API functions that look up a module in
the registry and then in `sys.modules`:

  >>> import zope.app.module
  >>> zope.app.module.findModule('mymodule') is module
  True
  >>> zope.app.module.findModule('zope.app.module') is zope.app.module
  True

The second function can be used to lookup objects inside any module:

  >>> zope.app.module.resolve('mymodule.foo')
  1
  >>> zope.app.module.resolve('zope.app.module.foo.resolve')

In order to use this framework in real Python code import statements, we need
to install the importer hook, which is commonly done with an event subscriber:

  >>> import __builtin__
  >>> event = object()
  >>> zope.app.module.installPersistentModuleImporter(event)
  >>> __builtin__.__import__ # doctest: +ELLIPSIS
  <bound method ZopePersistentModuleImporter.__import__ of ...>

Now we can simply import the persistent module:

  >>> import mymodule
  >>> mymodule.Blah('my id')
  Blah(id=my id)

Finally, we unregister the hook again:

  >>> zope.app.module.uninstallPersistentModuleImporter(event)
  >>> __builtin__.__import__
  <built-in function __import__>
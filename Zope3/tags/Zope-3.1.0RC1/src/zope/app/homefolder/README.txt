=====================
Principal Home Folder
=====================

The principal home folder subscriber lets you assign home folders to
principals as you would do in any OS. This particular implementation of such a
feature is intended as a demo of the power of the way to handle principals
and not as the holy grail. If you have concerns about the assumptions made in
this implementation (which are probably legitimate), just ignore this package
altogether.

Managing the Home Folders
-------------------------

Let's say we have a principal and we want to have a home folder for it. The
first task is to create the home folder manager, which keeps track of the
principal's home folders:

  >>> from zope.app.homefolder.homefolder import HomeFolderManager
  >>> manager = HomeFolderManager()

Now the manager will not be able to do much, because it does not know where to
look for the principal home folders. Therefore we have to specify a folder
container:

  >>> from zope.app.container.btree import BTreeContainer
  >>> baseFolder = BTreeContainer()
  >>> manager.homeFolderBase = baseFolder

Now we can assign a home folder to a principal:

  >>> manager.assignHomeFolder('stephan')

Since we did not specify the name of the home folder, it is just the same
as the principal id:

  >>> manager.assignments['stephan']
  'stephan'

Since the home folder did not exist and the `createHomeFolder` option was
turned on, the directory was created for you:

  >>> 'stephan' in baseFolder
  True

When creating the home folder, the principal also automatically receives the
`zope.Manager` role:

  >>> from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
  >>> roles = IPrincipalRoleManager(baseFolder['stephan'])
  >>> [(role, str(setting))
  ...  for role, setting in roles.getRolesForPrincipal('stephan')]
  [(u'zope.Manager', 'PermissionSetting: Allow')]

If a folder already exists for the provided name, then the creation is simply
skipped silently:

  >>> from zope.app.folder import Folder
  >>> baseFolder['sc3'] = Folder()
  >>> manager.assignHomeFolder('sc3')
  >>> manager.assignments['sc3']
  'sc3'

This has the advantage that you can choose your own `IContainer`
implementation instead of relying on the vanilla folder.

Now let's look at some derivations of the same task.

  1. Sometimes you want to specify an alternative folder name:

    >>> manager.assignHomeFolder('jim', folderName='J1m')
    >>> manager.assignments['jim']
    'J1m'
    >>> 'J1m' in baseFolder
    True

  2. Even though folders are created by default, you can specifically turn
     that behavior off for a particular assignment:

    >>> manager.assignHomeFolder('dreamcatcher', create=False)
    >>> manager.assignments['dreamcatcher']
    'dreamcatcher'
    >>> 'dreamcatcher' in baseFolder
    False

  3. You wish not to create a folder by default:

    >>> manager.createHomeFolder = False
    >>> manager.assignHomeFolder('philiKON')
    >>> manager.assignments['philiKON']
    'philiKON'
    >>> 'philiKON' in baseFolder
    False

  4. You do not want to create a folder by default, you want to create the
     folder for a specific user:

    >>> manager.assignHomeFolder('stevea', create=True)
    >>> manager.assignments['stevea']
    'stevea'
    >>> 'stevea' in baseFolder
    True

Let's now look at removing home folder assignments. By default, removing an
assignment will *not* delete the actual folder:

  >>> manager.unassignHomeFolder('stevea')
  >>> 'stevea' not in manager.assignments
  True
  >>> 'stevea' in baseFolder
  True

But if you specify the `delete` argument, then the folder will be deleted:

  >>> 'J1m' in baseFolder
  True
  >>> manager.unassignHomeFolder('jim', delete=True)
  >>> 'jim' not in manager.assignments
  True
  >>> 'J1m' in baseFolder
  False

Next, let's have a look at retrieving the home folder for a principal. This
can be done as follows:

  >>> homeFolder = manager.getHomeFolder('stephan')
  >>> homeFolder is baseFolder['stephan']
  True


If you try to get a folder and it does not yet exist, `None` will be
returned if autoCreateAssignment is False. Remember 'dreamcatcher', which 
has an assignment, but not a folder:

  >>> 'dreamcatcher' in baseFolder
  False
  >>> homeFolder = manager.getHomeFolder('dreamcatcher')
  >>> homeFolder is None
  True
  
However, if autoCreateAssignment is True and you try to get a home folder
of a principal which has no assignment, the assignment and the folder
will be automatically created. The folder will always be created, regardless
of the value of createHomeFolder. The name of the folder will be identically
to the principalId:

  >>> manager.autoCreateAssignment = True
  >>> homeFolder = manager.getHomeFolder('florian')
  >>> 'florian' in manager.assignments
  True
  >>> 'florian' in baseFolder
  True

Accessing the Home Folder
-------------------------

But how does the home folder get assigned to a principal? There are two ways
of accessing the homefolder. The first is via a simple adapter that provides a
`homeFolder` attribute. The second method provides the folder via a path
adapter called `homefolder`.

Let's start by creating a principal:

  >>> from zope.security.interfaces import IPrincipal
  >>> from zope.interface import implements
  >>> class Principal:
  ...     implements(IPrincipal)
  ...     def __init__(self, id):
  ...         self.id = id
  >>> principal = Principal('stephan')

We also need to register our manager as a utility:

  >>> from zope.app.testing import ztapi
  >>> from zope.app.homefolder.interfaces import IHomeFolderManager
  >>> ztapi.provideUtility(IHomeFolderManager, manager, 'manager')


(1) Now we can access the home folder via the adapter:

  >>> from zope.app.homefolder.interfaces import IHomeFolder
  >>> adapter = IHomeFolder(principal)
  >>> adapter.homeFolder is baseFolder['stephan']
  True

(2) Or alternatively via the path adapter:

  >>> from zope.app.traversing.interfaces import IPathAdapter
  >>> from zope.app import zapi
  >>> zapi.getAdapter(principal, IPathAdapter,
  ...                 "homefolder") is baseFolder['stephan']
  True

As you can see, the path adapter just returns the homefolder. This way we can
guarantee that the folder's full API is always available. Of course the real
way it will be used is via a TALES expression:

  Setup of the Engine

  >>> from zope.app.pagetemplate.engine import Engine
  >>> from zope.tales.tales import Context
  >>> context = Context(Engine, {'principal': principal})

  Executing the TALES expression

  >>> bytecode = Engine.compile('principal/homefolder:keys')
  >>> list(bytecode(context))
  []
  >>> baseFolder['stephan'][u'documents'] = Folder()
  >>> list(bytecode(context))
  [u'documents']

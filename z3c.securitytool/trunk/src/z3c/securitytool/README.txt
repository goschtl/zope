==============
z3c.securitytool
================


z3c.securitytool is a Zope3 package aimed at providing component level
security information to assist in analyzing security problems and to
potentially expose weaknesses. The goal of the security tool is to
provide a matrix of users and their effective permissions for all available
views for any given component and context. We also provide two further
levels of detail. You can view the details of how a user came to have
the permission on a given view, by clicking on the permission in the matrix.


FOR THE IMPATIENT TO VIEW YOUR SECURITY MATRIX:
  Remember this is a work in progress.

  1. Add the z3c.securitytool to your install_requires in your
     setup.py. 
  2. Add the <include package="z3c.securitytool"/> to your site.zcml
  3. Append the @@securityMatrix.html view to any context to view the permission
     matrix for that context.


  Desired Behavior
  ---------------
  On the page you will be able to select the desired skin from all the
  available skins on the system.  On initial load of the securitytool
  you will only see permissions for IBrowserRequest and your current 
  context. The interesting information is when you select the skins.
  A future release of this tool will offer a selection to view  all
  information for all skins as well as each skin individually.

  You can also truncate the results by selecting the permission from
  the filter select box.

  When you click on the "Allow" or "Deny" security tool will explain
  where these permissions were specified whether by role, group, or
  in local context.

  When you click on a user-name all the permissions inherited from
  roles, groups or specifically assigned will be displayed.


    >>> from pprint import pprint
    >>> import zope
    >>> from zope.interface import implements
    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zope.app.container import contained
    >>> from zope.app.folder import Folder, rootFolder
    >>> import persistent


    >>> from zope.app.authentication.principalfolder import Principal
    >>> from zope.securitypolicy.role import Role
    >>> from zope.security.permission import Permission

    >>> from zope.publisher.interfaces import IRequest

    >>> from zope.component import provideAdapter
    >>> from zope.app.testing import ztapi
    >>> from zope.app.folder.interfaces import IFolder
    >>> import transaction

    >>> from zope.app import zapi
    >>> principals = zapi.principals()
    >>> principals._clear()


The news agency, the Concord Times, is implementing a new article management
system in Zope 3. In order to better understand their security
situation they have installed z3c.security tool.

    >>> concordTimes = getRootFolder()

The Concord Times site is a folder which contains a Folder per issue
and  each issue contains articles.

    >>> class Issue(Folder):
    ...     implements(IFolder)
    ...     def __repr__(self):
    ...         return '<%s %r>' %(self.__class__.__name__, self.title)

    >>> ztapi.provideAdapter(
    ...     IRequest, IFolder,
    ...     Issue)

    >>> class Article(contained.Contained, persistent.Persistent):
    ...     implements(IAttributeAnnotatable)
    ...
    ...     def __init__(self, title, text):
    ...         self.title = title
    ...         self.text = text
    ...
    ...     def __repr__(self):
    ...         return '<%s %r>' %(self.__class__.__name__, self.title)

At the Concord Times, they have only three levels of users: Editors,
Writers, and Janitors.

    >>> editor = Role('concord.Editor', 'The editors')
    >>> writer = Role('concord.Writer', 'The writers')
    >>> janitor = Role('concord.Janitor', 'The janitors')

In order to control who has access to the system, they define the following
necessary permissions:

    >>> createIssue = Permission('concord.CreateIssue','Create Issue')
    >>> publishIssue = Permission('concord.PublishIssue', 'Publish Issue')
    >>> readIssue    = Permission('concord.ReadIssue', 'Read Issue')
    >>> createArticle = Permission('concord.CreateArticle', 'Create Article')
    >>> deleteArticle = Permission('concord.DeleteArticle', 'Delete Article')

Now we need to setup the security system on the level of the news agency.
In order to assign the permissions to the roles, we must setup a role-
permission Manager, which is used to map permissions to roles.

    >>> from zope.securitypolicy.interfaces import IRolePermissionManager
    >>> rolePermManager = IRolePermissionManager(concordTimes)

Now we can use our ``rolePermManager`` to assign the roles.
Editors are the only users that are allowed to create and publish issues.
Writers and Editors may create articles, but only editors can delete them.
Everyone can read the issues.

    >>> rolePermManager.grantPermissionToRole(createIssue.id, editor.id)
    >>> rolePermManager.grantPermissionToRole(publishIssue.id, editor.id)
    >>> rolePermManager.grantPermissionToRole(readIssue.id, editor.id)
    >>> rolePermManager.grantPermissionToRole(createArticle.id, editor.id)
    >>> rolePermManager.grantPermissionToRole(deleteArticle.id, editor.id)

    >>> rolePermManager.grantPermissionToRole(readIssue.id, writer.id)
    >>> rolePermManager.grantPermissionToRole(createArticle.id, writer.id)

    >>> rolePermManager.grantPermissionToRole(readIssue.id, janitor.id)

The news agency now hires the initial set of staff members. So let's create
a principal for each hired person:

    >>> martin = Principal('martin', 'Martin')
    >>> randy = Principal('randy', 'Randy')
    >>> markus = Principal('markus', 'Markus')
    >>> daniel = Principal('daniel', 'Daniel')
    >>> stephan = Principal('stephan', 'Stephan')

Based on their positions we assign proper roles to the staff.
In order to assign roles to our staff members, we must first create a
principal-role manager.

    >>> from zope.securitypolicy.interfaces import IPrincipalRoleManager
    >>> prinRoleManager = IPrincipalRoleManager(concordTimes)

And now we can assign the roles. At the Concord Times, Martin is an editor,
Randy and Markus are writers, and Daniel and Stephan are janitors.

    >>> prinRoleManager.assignRoleToPrincipal(editor.id, martin.id)
    >>> prinRoleManager.assignRoleToPrincipal(writer.id, randy.id)
    >>> prinRoleManager.assignRoleToPrincipal(writer.id, markus.id)
    >>> prinRoleManager.assignRoleToPrincipal(janitor.id, daniel.id)
    >>> prinRoleManager.assignRoleToPrincipal(janitor.id, stephan.id)

Lets set up the securityPolicy objects and the corresponding
participation for our actors.

    >>> from zope.security import testing
    >>> from zope.securitypolicy import zopepolicy

    >>> markus_policy = zopepolicy.ZopeSecurityPolicy()
    >>> markus_part = testing.Participation(markus)
    >>> markus_policy.add(markus_part)

    >>> martin_policy = zopepolicy.ZopeSecurityPolicy()
    >>> martin_part = testing.Participation(martin)
    >>> martin_policy.add(martin_part)

    >>> randy_policy = zopepolicy.ZopeSecurityPolicy()
    >>> randy_part = testing.Participation(randy)
    >>> randy_policy.add(randy_part)

    >>> stephan_policy = zopepolicy.ZopeSecurityPolicy()
    >>> stephan_part = testing.Participation(stephan)
    >>> stephan_policy.add(stephan_part)

    >>> daniel_policy = zopepolicy.ZopeSecurityPolicy()
    >>> daniel_part = testing.Participation(daniel)
    >>> daniel_policy.add(daniel_part)


    >>> firstIssue = \
    ...    Folder()
    >>> concordTimes['firstIssue'] = firstIssue
    >>> concordTimes._p_changed = 1
    >>> transaction.commit()

Randy starts to write his first article:

    >>> firstArticle = Article('A new star is born',
    ...                        'A new star is born, the `Concord Times` ...')

   TODO: add permission settings for this context then test with
   functional tests.

Markus tries to give his fellow writer some help by attempting to
create an Issue and of course cannot.

    >>> markus_policy.checkPermission(createIssue.id, concordTimes)
    False


Only Martin as the editor has createIssue privileges.

    >>> martin_policy.checkPermission(createIssue.id, concordTimes)
    True

    >>> list(concordTimes.keys())
    [u'firstIssue']


---------------------------------------------------------------------
To fully test the tool we added  the principals, permissions and roles
to the ftesting.zcml
---------------------------------------------------------------------

Okay, Now lets see what security tool thinks the user has assigned for
roles, permissions and groups.

    >>> from z3c.securitytool.interfaces import ISecurityChecker
    >>> principals = zapi.principals()
    >>> first = ISecurityChecker(firstIssue)


Lets get all the permission settings for the zope.interface.Interface
of course an empty set should get returned
    >>> first.getPermissionSettingsForAllViews(zope.interface.Interface)
    [{}, {}, set([])]

Lets see what our permission settings are for the concord Times folder
    >>> from zope.interface import providedBy
    >>> ifaces = tuple(providedBy(concordTimes))
    >>> permDetails = first.getPermissionSettingsForAllViews(ifaces)
    >>> pprint(permDetails)
    [{'daniel': {u'absolute_url': 'Allow', u'<i>no name</i>': 'Allow'},
      'markus': {u'absolute_url': 'Allow', u'<i>no name</i>': 'Allow'},
      'martin': {u'absolute_url': 'Allow', u'<i>no name</i>': 'Allow'},
      'randy': {u'absolute_url': 'Allow', u'<i>no name</i>': 'Allow'},
      'stephan': {u'absolute_url': 'Allow', u'<i>no name</i>': 'Allow'},
      'zope.anybody': {u'<i>no name</i>': 'Allow',
                       u'DELETE': 'Allow',
                       u'OPTIONS': 'Allow',
                       u'PUT': 'Allow',
                       u'absolute_url': 'Allow'},
      'zope.daniel': {u'<i>no name</i>': 'Allow',
                      u'DELETE': 'Allow',
                      u'OPTIONS': 'Allow',
                      u'PUT': 'Allow',
                      u'absolute_url': 'Allow'},
      'zope.markus': {u'<i>no name</i>': 'Allow',
                      u'DELETE': 'Allow',
                      u'OPTIONS': 'Allow',
                      u'PUT': 'Allow',
                      u'absolute_url': 'Allow'},
      'zope.martin': {u'<i>no name</i>': 'Allow',
                      u'DELETE': 'Allow',
                      u'OPTIONS': 'Allow',
                      u'PUT': 'Allow',
                      u'absolute_url': 'Allow'},
      'zope.randy': {u'<i>no name</i>': 'Allow',
                     u'DELETE': 'Allow',
                     u'OPTIONS': 'Allow',
                     u'PUT': 'Allow',
                     u'absolute_url': 'Allow'},
      'zope.sample_manager': {u'<i>no name</i>': 'Allow',
                              u'DELETE': 'Allow',
                              u'OPTIONS': 'Allow',
                              u'PUT': 'Allow',
                              u'absolute_url': 'Allow'},
      'zope.stephan': {u'<i>no name</i>': 'Allow',
                       u'DELETE': 'Allow',
                       u'OPTIONS': 'Allow',
                       u'PUT': 'Allow',
                       u'absolute_url': 'Allow'}},
     {u'<i>no name</i>': 'zope.Public',
      u'DELETE': 'zope.Public',
      u'OPTIONS': 'zope.Public',
      u'PUT': 'zope.Public',
      u'absolute_url': 'zope.Public'},
     set(['zope.Public'])]


Following are the helper functions used within the securitytool, These
contain a set of common functionality that is used in many places.



Lets see if the `hasPermissionSetting` method returns True if there is
a permission or role and False if there is not.
   >>> from z3c.securitytool.securitytool import *
   >>> hasPermissionSetting({'permissions':'Allow'})
   True

We need to make some dummy objects to test the `hasPermissionSetting` method
    >>> emptySettings = {'permissions': [],
    ...                  'roles': {},
    ...                  'groups': {}}

    >>> fullSettings = {'permissions': 'Allow',
    ...                  'roles': {},
    ...                  'groups': {}}

We also need to make sure the recursive functionality works for this method
     >>> hasPermissionSetting({'permissions':{},'roles':{},
     ...                                 'groups':{'group1':emptySettings,
     ...                                           'group2':fullSettings}})
     True

    >>> class SettingDummy(object):
    ...   def getName(self):
    ...     return 'Allow'

    >>> prinPermMap = ({'principal':'daniel',
    ...                 'permission':'takeOverTheWORLD',
    ...                 'setting':  SettingDummy()})

    >>> rolePermMap = ({'role':'Janitor',
    ...                 'permission':'takeOverTheWORLD',
    ...                 'setting':  SettingDummy()})

    >>> prinRoleMap = ({'principal':'daniel',
    ...                 'role':'Janitor',
    ...                 'setting':  SettingDummy()})



Lets test the method with our new dummy data
    >>> principalDirectlyProvidesPermission([prinPermMap],'daniel',
    ...                                          'takeOverTheWORLD')
    'Allow'

And we also need to test the roleProvidesPermission
    >>> roleProvidesPermission([rolePermMap], 'Janitor', 'takeOverTheWORLD')
    'Allow'

And we also need to test the roleProvidesPermission
    >>> principalRoleProvidesPermission([prinRoleMap],
    ...                                 [rolePermMap],
    ...                                 'daniel',
    ...                                 'takeOverTheWORLD')
    ('Janitor', 'Allow')

See janitors CAN take over the world!!!!!

And for a negative test
    >>> principalRoleProvidesPermission([prinRoleMap],
    ...                                 [rolePermMap],
    ...                                 'dummy',
    ...                                 'takeOverTheWORLD')
    (None, None)


And of course the rendered name to display on the page template
If we do not receive a name that means we are on the root level.
    >>> renderedName(None)
    u'Root Folder'

    >>> renderedName('Daniel')
    'Daniel'



    >>> first.populatePermissionMatrix('takeOverTheWORLD',[prinPermMap])



Now we test the meat of the SecurityChecker Class


    >>> settings = {'principalPermissions': [prinPermMap],
    ...             'rolePermissions'     : [rolePermMap],
    ...             'principalRoles'      : [prinRoleMap]}


    >>> first._permissionDetails(daniel, 'takeOverTheWORLD',
    ...                          [['viewName',settings]],[rolePermMap])
    {'groups': {},
     'roles': {'Janitor': [{'setting': 'Allow', 'name': 'viewName'}]},
     'permissions': [{'setting': 'Allow', 'name': 'viewName'}]}


Here we will test with the principal that was populated earlier.
    >>> daniel  = principals.definePrincipal('daniel','daniel','daniel')
    >>> pprint(first.principalPermissions('daniel') )
    {'groups': {},
     'permissions': [],
     'roles': {'concord.Janitor': [{'permission': 'concord.ReadIssue',
                                   'setting': 'Allow'}]}}


    >>> print first.permissionDetails('daniel', None)
    {'read_perm': 'zope.Public',
     'groups': {},
     'roles': {},
     'permissions': []}



Lets make sure all the views work properly. Just a simple smoke test

    >>> from zope.testbrowser.testing import Browser
    >>> manager = Browser()
    >>> authHeader = 'Basic mgr:mgrpw'
    >>> manager.addHeader('Authorization', authHeader)
    >>> manager.handleErrors = False


First we will check if the main page is available
    >>> manager.open('http://localhost:8080/@@securityMatrix.html')


Now lets send the filter variable so our test is complete
    >>> manager.open('http://localhost:8080/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes')


And with the selected permission
    >>> manager.open('http://localhost:8080/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes&'
    ...              'selectedPermission=zope.Public')


Here we send an invalid selectedPermisson ( just for coverage ) ;)
    >>> manager.open('http://localhost:8080/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes&'
    ...              'selectedPermission=zope.dummy')


This is the principal detail page, you can get to by clicking on the
principals name at the top of the form.
    >>> manager.open('http://localhost:8080/@@principalDetails.html?principal=daniel')
    >>> 'Permission settings' in manager.contents
    True


And lets call the view without a principal
    >>> manager.open('http://localhost:8080/@@principalDetails.html')
    Traceback (most recent call last):
    ...
    PrincipalLookupError: no principal specified

Here is the view you will see if you click on the actual permission
value in the matrix intersecting the view to the user on a public view.
    >>> manager.open('http://localhost:8080/@@permissionDetails.html?'
    ...              'principal=daniel&view=PUT')

    >>> 'zope.Public' in manager.contents
    True

Ok lets send the command without the principal:
    >>> manager.open('http://localhost:8080/@@permissionDetails.html?view=PUT')
    Traceback (most recent call last):
    ...
    PrincipalLookupError: no user specified

And now we will test it without the view name
  >>> manager.open('http://localhost:8080/@@permissionDetails.html?principal=daniel')


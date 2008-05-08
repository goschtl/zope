======================
Detailed Documentation
======================

On the main  page of the securityTool you will be able to select
the desired skin from all the available skins on the system.
On initial load of the securitytool you will only see permissions
for IBrowserRequest and your current context. The interesting
information is when you select the skins. A future release of
this tool will offer a selection to view  all information for all
skins as well as each skin individually. You can also truncate the
results by selecting the permission from the filter select box.
When you click on the "Allow" or "Deny" security tool will explain
where these permissions were specified whether by role, group, or
in local context.

When you click on a user-name all the permissions inherited from
roles, groups or specifically assigned permissions will be displayed.

    >>> import zope
    >>> from zope.app import zapi
    >>> from pprint import pprint
    >>> from zope.interface import providedBy
    >>> from z3c.securitytool.securitytool import getViews
    >>> from z3c.securitytool.interfaces import ISecurityChecker
    >>> from z3c.securitytool.interfaces import IPrincipalDetails
    >>> from z3c.securitytool.interfaces import IPermissionDetails
    >>> root = getRootFolder()

Several things are added to the database on the IDatabaseOpenedEvent when
starting the demo or running the tests. These settings are used to test
the functionality in the tests as well as populate a matrix for the demo.
Lets make sure the items were added with demoSetup.py

    >>> sorted(root.keys())
    [u'Folder1']

To retrieve the permission settings for the folder we must first adapt the
context to a SecurityChecker Object.

    >>> folder1 = ISecurityChecker(root['Folder1'])

    >>> pprint(dir(folder1))
    ['__class__',
     '__component_adapts__',
    ...
     'aggregateMatrices',
     'context',
     'getPermissionSettingsForAllViews',
     'getReadPerm',
     'populateMatrix',
     'populatePermissionMatrix',
     'updateRolePermissionSetting']
        

Ok. Lets now see how the security tool represents the permissions for
a certain context level and Interface.

The `getPermissionSettingsForAllViews` method takes a tuple of interfaces
as an argument to determine what views registered at this context level.

Since nothing should be registerd for only zope.interface.Interface we
should recieve an empty set, of permissions, roles and groups.
    >>> folder1.getPermissionSettingsForAllViews(zope.interface.Interface)
    [{}, {}, set([])]


We first get the interfaces registered for this context
level and then list all the view names that are registered for this context
and Interface.

Now lets see what the actual securityMatrix looks like in the context level
of folder1.
    >>> ifaces = tuple(providedBy(folder1))
    >>> pprint(ifaces)
    (<InterfaceClass z3c.securitytool.interfaces.ISecurityChecker>,)

    >>> pprint(sorted([x.name for x in getViews(ifaces[0])]))
    [u'acquire',
     u'adapter',
     u'attribute',
     u'etc',
     u'item',
     u'lang',
     u'resource',
     u'skin',
     u'vh',
     u'view']

The following data structure returned from getPermissionSettingsForAllViews
is used to populate the main securitytool page.

    >>> permDetails = folder1.getPermissionSettingsForAllViews(ifaces)
    >>> pprint(permDetails)
     [{'zope.anybody': {u'<i>no name</i>': 'Allow',
                            u'DELETE': 'Allow',
                          u'OPTIONS': 'Allow',
                          u'PUT': 'Allow',
                          u'absolute_url': 'Allow'},
         'zope.daniel': {u'<i>no name</i>': 'Allow',
                         u'DELETE': 'Allow',
                         u'OPTIONS': 'Allow',
                         u'PUT': 'Allow',
                         u'absolute_url': 'Allow'},
         'zope.globalmgr': {u'<i>no name</i>': 'Allow',
                            u'DELETE': 'Allow',
                            u'OPTIONS': 'Allow',
                            u'PUT': 'Allow',
                            u'absolute_url': 'Allow'},
         'zope.group1': {u'absolute_url': 'Allow', u'<i>no name</i>': 'Allow'},
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
         'zope.mgr': {u'absolute_url': 'Allow', u'<i>no name</i>': 'Allow'},
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

    >>> from zope.securitypolicy.interfaces import Allow, Unset, Deny

    >>> prinPermMap = ({'principal':'daniel',
    ...                 'permission':'takeOverTheWORLD',
    ...                 'setting':  Allow})

    >>> rolePermMap = ({'role':'Janitor',
    ...                 'permission':'takeOverTheWORLD',
    ...                 'setting':  Allow})

    >>> prinRoleMap = ({'principal':'daniel',
    ...                 'role':'Janitor',
    ...                 'setting':  Allow})


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

And of course the rendered name to display on the page template
If we do not receive a name that means we are on the root level.

    >>> renderedName(None)
    u'Root Folder'

    >>> renderedName('Daniel')
    'Daniel'

    >>> folder1.populatePermissionMatrix('takeOverTheWORLD',[prinPermMap])

Now we test the meat of the SecurityChecker Class

    >>> settings = {'principalPermissions': [prinPermMap],
    ...             'rolePermissions'     : [rolePermMap],
    ...             'principalRoles'      : [prinRoleMap]}


    >>> permDetails = PermissionDetails(folder1)

Lets see what the principalDetails look like for the principal Daniel
and the context of 'Folder1'.

    >>> prinDetails = PrincipalDetails(root[u'Folder1'])
    >>> matrix = prinDetails('zope.daniel')
    >>> pprint(matrix['groups'])
    {'zope.group1':
          {'groups': {},
            'permissionTree': [{u'Folder1_2': {'name': None,
                        'parentList': [u'Folder1',
                               'Root Folder'],
                        'permissions': [{'permission': 'concord.CreateArticle',
                                'principal': 'zope.group1',
                                'setting': PermissionSetting: Allow},
                                {'permission': 'concord.ReadIssue',
                                'principal': 'zope.group1',
                                'setting': PermissionSetting: Deny},
                                {'permission': 'concord.DeleteIssue',
                                'principal': 'zope.group1',
                                'setting': PermissionSetting: Allow}]}},
                {'Root Folder': {'name': 'Root Folder',
                         'parentList': ['Root Folder'],
                         'permissions': [{'permission': 'concord.CreateArticle',
                                 'principal': 'zope.group1',
                                 'setting': PermissionSetting: Deny},
                                 {'permission': 'concord.ReadIssue',
                                 'principal': 'zope.group1',
                                 'setting': PermissionSetting: Allow},
                                 {'permission': 'concord.DeleteArticle',
                                 'principal': 'zope.group1',
                                 'setting': PermissionSetting: Deny}]}}],
      'permissions': [{'permission': 'concord.CreateArticle',
               'setting': PermissionSetting: Allow},
              {'permission': 'concord.ReadIssue',
               'setting': PermissionSetting: Deny},
              {'permission': 'concord.DeleteIssue',
               'setting': PermissionSetting: Allow},
              {'permission': 'concord.DeleteArticle',
               'setting': PermissionSetting: Deny}],
      'roleTree': [{'Root Folder': {'name': 'Root Folder',
                      'parentList': ['Root Folder'],
                      'roles': [{'principal': 'zope.group1',
                           'role': 'zope.Editor',
                           'setting': PermissionSetting: Allow}]}}],
      'roles': {'zope.Editor': [{'permission': 'concord.CreateIssue',
                    'setting': 'Allow'},
                   {'permission': 'concord.DeleteArticle',
                    'setting': 'Allow'},
                   {'permission': 'concord.PublishIssue',
                    'setting': 'Allow'},
                   {'permission': 'concord.DeleteIssue',
                    'setting': 'Allow'},
                   {'permission': 'concord.CreateArticle',
                    'setting': 'Allow'},
                   {'permission': 'concord.ReadIssue',
                    'setting': 'Allow'}]}}}

    >>> pprint(matrix['permissionTree'])
    [{u'Folder1_2': {'name': None,
                     'parentList': [u'Folder1', 'Root Folder'],
                     'permissions': [{'permission': 'concord.CreateArticle',
                                      'principal': 'zope.daniel',
                                      'setting': PermissionSetting: Allow},
                                     {'permission': 'concord.ReadIssue',
                                      'principal': 'zope.daniel',
                                      'setting': PermissionSetting: Deny},
                                     {'permission': 'concord.DeleteIssue',
                                      'principal': 'zope.daniel',
                                      'setting': PermissionSetting: Allow}]}},
     {'Root  Folder': {'name': 'Root  Folder',
                       'parentList': ['Root Folder'],
                       'permissions': [{'permission': 'concord.CreateArticle',
                                        'principal': 'zope.daniel',
                                        'setting': PermissionSetting: Deny},
                                       {'permission': 'concord.ReadIssue',
                                        'principal': 'zope.daniel',
                                        'setting': PermissionSetting: Allow},
                                       {'permission': 'concord.DeleteArticle',
                                        'principal': 'zope.daniel',
                                        'setting': PermissionSetting: Deny}]}}]

    >>> pprint(matrix['permissions'])
    [{'setting': PermissionSetting: Allow,
      'permission': 'concord.CreateArticle'},
     {'setting': PermissionSetting: Deny,
      'permission': 'concord.ReadIssue'},
     {'setting': PermissionSetting: Allow,
      'permission': 'concord.DeleteIssue'},
     {'setting': PermissionSetting: Deny,
      'permission': 'concord.DeleteArticle'}]

The roleTree is stored as a list so to consistently view the data
properly we will create a dictionary out of it.    

    >>> tmpDict = {}
    >>> keys = matrix['roleTree']
    >>> for item in matrix['roleTree']:
    ...     tmpDict.update(item)

    >>> pprint(tmpDict['Root Folder'])
    {'name': 'Root Folder',
     'parentList': ['Root Folder'],
     'roles': [{'principal': 'zope.daniel',
                'role': 'zope.Writer',
                'setting': PermissionSetting: Allow}]}
    
    >>> pprint(tmpDict['Folder1_2'])
    {'name': None,
     'parentList': [u'Folder1', 'Root Folder'],
     'roles': [{'principal': 'zope.daniel',
                'role': 'zope.Writer',
                'setting': PermissionSetting: Allow}]}

    >>> pprint(tmpDict['global settings'])
    {'name': None,
     'parentList': ['global settings'],
     'roles': [{'principal': 'zope.daniel',
                'role': 'zope.Janitor',
                'setting': PermissionSetting: Allow}]}

    >>> pprint(matrix['roles'])
    {'zope.Janitor': [{'setting': 'Allow', 'permission': 'concord.ReadIssue'}],
     'zope.Writer': [{'setting': 'Allow', 'permission': 'concord.DeleteArticle'},
                     {'setting': 'Allow', 'permission': 'concord.CreateArticle'},
                     {'setting': 'Allow', 'permission': 'concord.ReadIssue'}]}
    

Now lets see what the permission details returns
    >>> from zope.publisher.interfaces.browser import IBrowserRequest
    >>> from z3c.securitytool.interfaces import IPermissionDetails
    >>> permAdapter = zapi.getMultiAdapter((root[u'Folder1'],
    ...                             ),IPermissionDetails)
    >>> prinPerms  = permAdapter('zope.daniel',
    ...                          'ReadIssue.html',
    ...                           )

    >>> print permAdapter.skin
    <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>

    >>> print permAdapter.read_perm
    zope.Public

    >>> print permAdapter.view_name
    ReadIssue.html

    >>> pprint(prinPerms)
    {'groups': {'zope.group1': {'groups': {},
                                'permissionTree': [],
                                'permissions': [],
                                'roleTree': [],
                                'roles': {}}},
     'permissionTree': [],
     'permissions': [],
     'roleTree': [],
     'roles': {}}

TestBrowser Smoke Tests
-----------------------

Lets make sure all the views work properly. Just a simple smoke test

    >>> from zope.testbrowser.testing import Browser
    >>> manager = Browser()
    >>> authHeader = 'Basic mgr:mgrpw'
    >>> manager.addHeader('Authorization', authHeader)
    >>> manager.handleErrors = False

    >>> server = 'http://localhost:8080/++skin++SecurityTool'

    >>> manager.open(server + '/@@securityMatrix.html')

First we will check if the main page is available
    >>> manager.open(server + '/@@securityMatrix.html')

    >>> manager.open(server + '/Folder1/@@securityMatrix.html')

    >>> manager.open(server + '/Folder1/Folder2/Folder3/@@securityMatrix.html')

Now lets send the filter variable so our test is complete
    >>> manager.open(server + '/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes')


And with the selected permission

    >>> manager.open(server + '/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes&'
    ...              'selectedPermission=zope.Public')


Here we send an invalid selectedPermisson ( just for coverage ) ;)
    >>> manager.open(server + '/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes&'
    ...              'selectedPermission=zope.dummy')

And with the None permission
    >>> manager.open(server + '/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes&'
    ...              'selectedPermission=None')

This is the principal detail page, you can get to by clicking on the
principals name at the top of the form

    >>> manager.open(server + 
    ...              '/@@principalDetails.html?principal=zope.daniel')

    >>> manager.open(server + 
    ...              '/Folder1/Folder2/Folder3/'
    ...              '@@principalDetails.html?principal=zope.daniel')


    >>> 'Permission settings' in manager.contents
    True


And lets call the view without a principal

    >>> manager.open(server + '/@@principalDetails.html')
    Traceback (most recent call last):
    ...
    PrincipalLookupError: no principal specified

Here is the view you will see if you click on the actual permission
value in the matrix intersecting the view to the user on a public view.

    >>> manager.open(server + '/@@permissionDetails.html?'
    ...              'principal=zope.daniel&view=PUT')

Ok lets send the command without the principal

    >>> manager.open(server + '/@@permissionDetails.html?view=PUT')
    Traceback (most recent call last):
    ...
    PrincipalLookupError: no user specified
 

And now we will test it without the view name

  >>> manager.open(server + '/@@permissionDetails.html?'
  ...                        'principal=zope.daniel')

And now with a view name that does not exist

  >>> manager.open(server + '/@@permissionDetails.html?'
  ...              'principal=zope.daniel&view=garbage')

Lets also test with a different context level

  >>> manager.open(server + 
  ...              '/Folder1/Folder2/Folder3/'
  ...              '@@permissionDetails.html'
  ...              '?principal=zope.daniel&view=ReadIssue.html')



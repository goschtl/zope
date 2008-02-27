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


    >>> import zope
    >>> from zope.app import zapi
    >>> from pprint import pprint

    >>> from z3c.securitytool.interfaces import ISecurityChecker
    >>> from z3c.securitytool.interfaces import IPrincipalDetails
    >>> from z3c.securitytool.interfaces import IPermissionDetails

 
    >>> root = getRootFolder()

Lets make sure the items were added with demoSetup.py
    >>> sorted(root.keys())
    [u'Folder1']

    >>> folder1 = ISecurityChecker(root['Folder1'])

We can see that the permissions for zope.interface.Interface should
return an empty set.
    >>> folder1.getPermissionSettingsForAllViews(zope.interface.Interface)
    [{}, {}, set([])]
        

    >>> from zope.interface import providedBy
    >>> ifaces = tuple(providedBy(folder1))
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

        permDetails(daniel, 'takeOverTheWorld',IBrowserRequest)
    {'groups': {},
     'roles': {'Janitor': [{'setting': 'Allow', 'name': 'viewName'}]},
     'permissions': [{'setting': 'Allow', 'name': 'viewName'}]}


Here we will test with the principal that was populated earlier.
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
    

Lets make sure all the views work properly. Just a simple smoke test

    >>> from zope.testbrowser.testing import Browser
    >>> manager = Browser()
    >>> authHeader = 'Basic mgr:mgrpw'
    >>> manager.addHeader('Authorization', authHeader)
    >>> manager.handleErrors = False


First we will check if the main page is available
    >>> manager.open('http://localhost:8080/@@securityMatrix.html')

    >>> manager.open('http://localhost:8080/Folder1/@@securityMatrix.html')

    >>> manager.open('http://localhost:8080/Folder1/Folder2/Folder3/@@securityMatrix.html')

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

And with the None permission
    >>> manager.open('http://localhost:8080/@@securityMatrix.html?'
    ...              'FILTER=None&selectedSkin=ConcordTimes&'
    ...              'selectedPermission=None')

This is the principal detail page, you can get to by clicking on the
principals name at the top of the form.

    >>> manager.open('http://localhost:8080/@@principalDetails.html?principal=zope.daniel')

    >>> manager.open('http://localhost:8080/Folder1/Folder2/Folder3/@@principalDetails.html?principal=zope.daniel')


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
    ...              'principal=zope.daniel&view=PUT')

    'zope.Public' in manager.contents
    True

Ok lets send the command without the principal:
    >>> manager.open('http://localhost:8080/@@permissionDetails.html?view=PUT')
    Traceback (most recent call last):
    ...
    PrincipalLookupError: no user specified

And now we will test it without the view name
  >>> manager.open('http://localhost:8080/@@permissionDetails.html?principal=zope.daniel')


And now with a view name that does not exist
  >>> manager.open('http://localhost:8080/@@permissionDetails.html?principal=zope.daniel&view=garbage')

Lets also test with a different context level
  >>> manager.open('http://localhost:8080/Folder1/Folder2/Folder3/@@permissionDetails.html?principal=zope.daniel&view=ReadIssue.html')

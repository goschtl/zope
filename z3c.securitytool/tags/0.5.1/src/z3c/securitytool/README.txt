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
    >>> from z3c.securitytool.securitytool import *
    >>> from z3c.securitytool.interfaces import ISecurityChecker
    >>> from z3c.securitytool.interfaces import IPrincipalDetails
    >>> from z3c.securitytool.interfaces import IPermissionDetails
    >>> from z3c.securitytool.browser import ISecurityToolSkin
    >>> root = getRootFolder()

    Several things are added to the database on the IDatabaseOpenedEvent when
    starting the demo or running the tests. These settings are used to test
    the functionality in the tests as well as populate a matrix for the demo.
    Lets make sure the items were added with demoSetup.py, We will assume
    that if Folder1 exists in the root folder then demoSetup.py was executed.

    >>> sorted(root.keys())
    [u'Folder1']

    To retrieve the permission settings for the folder we must first adapt the
    context to a SecurityChecker Object.

    >>> folder1 = ISecurityChecker(root['Folder1'])

    >>> print folder1.__class__.__name__
    SecurityChecker

    Lets introspect the object.

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
     'populateViewRoleMatrix']


    To get all the security settings for particular context level the
    getPermissionSettingsForAllViews is called with a tuple of interfaces.
    All the views registered for the interfaces passed will be inspected.

    Since nothing should be registered for only zope.interface.Interface we
    should receive an empty set, of permissions, roles and groups.

    >>> folder1.getPermissionSettingsForAllViews(zope.interface.Interface)
    [{}, {}, set([])]

    A realistic test would be to get all the interfaces provided by a specific
    context level like `Folder1`. Being a folder these are the interfaces as you
    might expect.

    >>> ifaces = tuple(providedBy(root['Folder1']))
    >>> pprint(ifaces)
    (<InterfaceClass zope.site.interfaces.IFolder>,
     <InterfaceClass zope.container.interfaces.IContentContainer>,
     <InterfaceClass persistent.interfaces.IPersistent>,
     <InterfaceClass zope.location.interfaces.IContained>,
     <InterfaceClass zope.component.interfaces.IPossibleSite>)

    The next step to determine security levels is the getViews function.
    `getViews` gets all the registered views for this interface. This
    is refined later to the views that are only accessible in this context.

    >>> pprint(sorted([x for x in getViews(ifaces[0])]))
    [AdapterRegistration... ITraversable, u'acquire', ...
     AdapterRegistration... ITraversable, u'adapter', ...
     AdapterRegistration... ITraversable, u'attribute', ...
     AdapterRegistration... ITraversable, u'etc', ...
     AdapterRegistration... ITraversable, u'item', ...
     AdapterRegistration... ITraversable, u'lang', ...
     AdapterRegistration... ITraversable, u'resource', ...
     AdapterRegistration... ITraversable, u'skin', ...
     AdapterRegistration... ITraversable, u'vh', ...
     AdapterRegistration... ITraversable, u'view', ...


    Since this is a large result set returned we will only test enough
    pieces of the results to inform of the desired behavior and to make sure
    the results are sane.

    >>> permDetails = folder1.getPermissionSettingsForAllViews(ifaces,
    ...                                                     ISecurityToolSkin)

    By using the ISecurityToolSkin we can see the actual securityTool
    views. The securityTool views are only registered for the
    ISecurityToolSkin layer.

    >>> pprint(permDetails)
    [...
      'zope.globalmgr': {u'<i>no name</i>': 'Allow',
                         u'DELETE': 'Allow',
                         u'OPTIONS': 'Allow',
                         u'PUT': 'Allow',
                         u'absolute_url': 'Allow',
                         u'permissionDetails.html': 'Allow',
                         u'principalDetails.html': 'Allow',
                         u'securityMatrix.html': 'Allow'},
    ...]

    As you can see below the `zope.anybody` has the 'Allow' permission
    for the four views listed below. The securitytool views are not listed
    here because they are neither specifically denied or allowed for
    this principal.

    >>> pprint(permDetails)
    ...
    [{'zope.anybody': {u'<i>no name</i>': 'Allow',
                      u'DELETE': 'Allow',
                      u'OPTIONS': 'Allow',
                      u'PUT': 'Allow',
                      u'absolute_url': 'Allow'},
    ...

    Another section of the result set shows all valid views for this
    context and skin, along with the permission required for access to
    the view.

    >>> pprint(permDetails)
    [...
    {u'<i>no name</i>': 'zope.Public',
      u'DELETE': 'zope.Public',
      u'OPTIONS': 'zope.Public',
      u'PUT': 'zope.Public',
      u'absolute_url': 'zope.Public',
      u'permissionDetails.html': 'zope.ManageContent',
      u'principalDetails.html': 'zope.ManageContent',
      u'securityMatrix.html': 'zope.ManageContent'},
    ...]

    All the principals in the system  are in this data structure.
    Here we just print a subset of the structure, to make sure the
    data is sane.

    >>> pprint(sorted(permDetails[0].keys()))
    ['zope.anybody',
     'zope.daniel',
     'zope.globalmgr',
     'zope.group1',
     'zope.markus',
     'zope.martin',
     'zope.mgr',
     'zope.randy',
     'zope.sample_manager',
     'zope.stephan']

    This of course should be identical to the users on the system from
    zapi.getPrincipals() without (zope.anybody)

    >>> from zope.app import zapi
    >>> sysPrincipals = zapi.principals()
    >>> principals = [x.id for x in sysPrincipals.getPrincipals('')]
    >>> pprint(sorted(principals))
    ['zope.daniel',
     'zope.globalmgr',
     'zope.group1',
     'zope.group2',
     'zope.markus',
     'zope.martin',
     'zope.mgr',
     'zope.randy',
     'zope.sample_manager',
     'zope.stephan']

========================================
Using securitytool to inspect principals
========================================

Lets see what the principalDetails look like for the principal Daniel
and the context of 'Folder1'.

    First we retrieve the principalDetails for Folder1:

    >>> prinDetails = PrincipalDetails(root[u'Folder1'])

    Then we filter out the uninteresting information for the user
    being inspected.

    >>> matrix = prinDetails('zope.daniel')

    The principal details structure contains five interesting pieces of data.

    >>> pprint(sorted(matrix.keys()))
    ['groups', 'permissionTree', 'permissions', 'roleTree', 'roles']

    Below we check to make sure the groups data structure from the user daniel
    is returned as expected. This is the data used to populate the groups
    section on the User Details page.

    >>> pprint(matrix['groups'].keys())
    ['zope.randy']

    The permission tree is used to display the levels of inheritance that were
    traversed to attain the permission displayed. The permission is
    stored as a list so the order is maintained. (yes I know there are
    better ways to accomplish this)

    >>> pprint(matrix['permissionTree'][0])
    {u'Folder1_2': {'name': None,
                     'parentList': [u'Folder1', 'Root Folder'],
                     'permissions': [{'permission': 'concord.CreateArticle',
                                      'principal': 'zope.daniel',
                                      'setting': PermissionSetting: Allow},
                                     {'permission': 'concord.ReadIssue',
                                      'principal': 'zope.daniel',
                                      'setting': PermissionSetting: Deny},
                                     {'permission': 'concord.DeleteIssue',
                                      'principal': 'zope.daniel',
                                      'setting': PermissionSetting: Allow}]}}


    >>> pprint(matrix['permissionTree'][1])
    {'Root Folder': {'name': 'Root Folder',
                     'parentList': ['Root Folder'],
                     'permissions': [{'permission': 'concord.DeleteArticle',
                                      'principal': 'zope.daniel',
                                      'setting': PermissionSetting: Deny},
                                     {'permission': 'concord.CreateArticle',
                                      'principal': 'zope.daniel',
                                      'setting': PermissionSetting: Deny},
                                     {'permission': 'concord.ReadIssue',
                                      'principal': 'zope.daniel',
                                      'setting': PermissionSetting: Allow}]}}


    The permissions section of the matrix displays the final say on
    whether or not the user has permissions at this context level.

    >>> pprint(matrix['permissions'], width=1)
    [{'permission': 'concord.CreateArticle',
      'setting': PermissionSetting: Allow},
     {'permission': 'concord.ReadIssue',
      'setting': PermissionSetting: Deny},
     {'permission': 'concord.DeleteIssue',
      'setting': PermissionSetting: Allow},
     {'permission': 'concord.DeleteArticle',
      'setting': PermissionSetting: Deny},
     {'permission': 'concord.CreateIssue',
      'setting': PermissionSetting: Allow},
     {'permission': 'concord.PublishIssue',
      'setting': PermissionSetting: Allow}]

    The roleTree structure is used to display the roles attained at
    each level of traversal. The roleTree is stored as a list so to
    consistently test the data properly we will create a dictionary
    out of it and is similar in function to the permissionTree.

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

    The roles section of the matrix displays the final say on whether or
    not the user has the role assigned at this context level.

    >>> pprint(matrix['roles'], width=1)
    {'zope.Janitor': [{'permission': 'concord.ReadIssue',
                       'setting': 'Allow'}],
     'zope.Writer': [{'permission': 'concord.DeleteArticle',
                      'setting': 'Allow'},
                     {'permission': 'concord.CreateArticle',
                      'setting': 'Allow'},
                     {'permission': 'concord.ReadIssue',
                      'setting': 'Allow'}]}


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
    {'groups': {'zope.randy': {'groups': {'zope.group1': {'groups': {},
                                                          'permissionTree': [],
                                                          'permissions': [],
                                                          'roleTree': [],
                                                          'roles': {}},
                                          'zope.group2': {'groups': {},
                                                          'permissionTree': [],
                                                          'permissions': [],
                                                          'roleTree': [],
                                                          'roles': {}}},
                               'permissionTree': [],
                               'permissions': [],
                               'roleTree': [],
                               'roles': {}}},
     'permissionTree': [],
     'permissions': [],
     'roleTree': [],
     'roles': {}}

Following are the helper functions used within the securitytool, These
contain a set of common functionality that is used in many places.
Lets see if the 'hasPermissionSetting' method returns True if there is
a permission or role and False if there is not.

   >>> hasPermissionSetting({'permissions':'Allow'})
   True

   We need to make some dummy objects to test the 'hasPermissionSetting' method

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

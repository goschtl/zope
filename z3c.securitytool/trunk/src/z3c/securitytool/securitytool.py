from zope.app import zapi
from zope.app.apidoc.presentation import getViewInfoDictionary
from zope.component import adapts, getGlobalSiteManager
from zope.i18nmessageid import ZopeMessageFactory as _
from zope.interface import Interface, implements, providedBy
from zope.publisher.browser import TestRequest, applySkin
from zope.publisher.interfaces import IRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.securitypolicy.interfaces import Allow, Unset, Deny
from zope.securitypolicy.interfaces import IPrincipalPermissionMap
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.securitypolicy.interfaces import IRolePermissionMap
from zope.securitypolicy.principalpermission import principalPermissionManager
from zope.securitypolicy.principalrole import principalRoleManager
from zope.securitypolicy.rolepermission import rolePermissionManager

from z3c.securitytool import interfaces

class SecurityChecker(object):
    """ Workhorse of the security tool package"""
    implements(interfaces.ISecurityChecker)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def getPermissionSettingsForAllViews(self,interfaces,
                                         skin=IBrowserRequest,
                                         selectedPermission=None):
        """ retrieves permission settings for all views"""
        request = TestRequest()
        self.selectedPermission = selectedPermission
        
        applySkin(request, skin)

        self.viewMatrix = {}
        self.viewPermMatrix = {}
        self.viewRoleMatrix = {}
        self.views = {}
        self.permissions = set()

        for iface in interfaces:
            for view_reg in getViews(iface, skin):
                viewInstance = getView(self.context, view_reg, skin)
                if viewInstance:
                    self.populateMatrix(viewInstance,view_reg)

        self.aggregateMatrices()
        return [self.viewMatrix,self.views,self.permissions]

    def aggregateMatrices(self):
        """
        This method is used to aggregate the two matricies together.
        There is a role matrix and a permission matrix. The reason for
        the role matrix is that we can have lower level assignments to
        override higher level assingments seperately from the direct
        assignments of permissions. We need to merge these together to
        have a complete matrix, When there is a conflict between
        permissions and role-permissions  permissions will always win.
        """

        # Populate the viewMatrix with the permissions gained from the
        # assigned roles
        for item in self.viewRoleMatrix:
            if not  self.viewMatrix.has_key(item):
                self.viewMatrix[item] = {}
            for viewSetting in self.viewRoleMatrix[item]:
                val = self.viewRoleMatrix[item][viewSetting] \
                                               and 'Allow' or '--'
                self.viewMatrix[item].update({viewSetting:val})

        # Populate the viewMatrix with the permissions directly assinged.
        for item in self.viewPermMatrix:
            if not  self.viewMatrix.has_key(item):
                self.viewMatrix[item] = {}
            for viewSetting in self.viewPermMatrix[item]:
                self.viewMatrix[item].update(
                      {viewSetting:self.viewPermMatrix[item][viewSetting]})

        # Now we will inherit the permissions from groups assigned to each
        # principal
        principals = zapi.principals()
        getPrin = principals.getPrincipal
        viewPrins = [getPrin(prin) for prin in self.viewMatrix]
        mergePermissionsFromGroups(viewPrins,self.viewMatrix)

    def getReadPerm(self,view_reg):
        """ Helper method which returns read_perm and view name"""
        info = getViewInfoDictionary(view_reg)
        read_perm = info['read_perm']
        if read_perm == None:
            read_perm = 'zope.Public'

        self.permissions.add(read_perm)
        name = info['name']

        return name, read_perm

    def populateMatrix(self,viewInstance,view_reg):
        """ populates the matrix used for the securityMatrix view"""

        self.name, read_perm = self.getReadPerm(view_reg)

        if self.selectedPermission and self.selectedPermission != read_perm:
            return
        self.views[self.name] = read_perm

        allSettings, settings = getSettingsForMatrix(viewInstance)
        rolePermMap = allSettings.get('rolePermissions', ())

        for name,setting in settings:
            principalRoles = setting.get('principalRoles', [])
            for role in principalRoles:
                principal = role['principal']

                if not self.viewRoleMatrix.has_key(principal):
                    self.viewRoleMatrix[principal] = {}
                if read_perm == 'zope.Public':
                    permSetting = (role,'Allow')

                elif role['setting'] == Deny:
                    #If the role has a setting and it is Deny.
                    try:
                        # Here we see if we have added a security setting with
                        # this role before, if it is now denied we remove it.
                        del self.viewRoleMatrix[principal]\
                                       [self.name][role['role']]
                    except KeyError:
                        pass

                else:
                    # The role has a setting and is Allow so we add it to the
                    # matrix.
                    permSetting =  principalRoleProvidesPermission(
                                   principalRoles, rolePermMap,
                                   principal, read_perm,
                                   role['role']
                                )
                if permSetting[1]:
                    self.updateRolePermissionSetting(permSetting[1],
                                                     principal,
                                                     role['role'],
                                                     self.name)

            prinPermissions = allSettings.get('principalPermissions',[])
            self.populatePermissionMatrix(read_perm,prinPermissions)

    def updateRolePermissionSetting(self,permSetting,principal,role,name):
        """
        Updates permission setting for current role if necessary this
        populates the viewRoleMatrix which is used with viewPermMatrix to
        determine the objects permission for the securityMatrix.html page

        """
        if permSetting != 'Deny':
            self.viewRoleMatrix[principal].setdefault(name,{})
            self.viewRoleMatrix[principal][name].update({role:permSetting})

    def populatePermissionMatrix(self,read_perm,principalPermissions):
        """ This method populates the principal permission section of
            the view matrix, it is half responsible for the 'Allow' and
            'Deny' on the securityMatrix.html page. The other half belongs
            to the role permissions (viewRoleMatrix).
        """

        matrix = self.viewPermMatrix
        principalPermissions.reverse()


        for prinPerm in principalPermissions:
            if prinPerm['permission'] != read_perm:
                #If it is not the read_perm it is uninteresting
                continue

            principal_id = prinPerm['principal']
            setting = prinPerm['setting'].getName()

            if matrix.setdefault(principal_id,{self.name:setting}) == \
                                                 {self.name:setting}:
                #If the principal_id is not in the matrix add it
                continue

            elif  matrix[principal_id].setdefault(
                         self.name,setting) == setting:
                #If the permisison does not exist for the prin add it
                continue

class MatrixDetails(object):
    """
    This class creates the complex permissionDetails object
    """

    def __init__(self,context):
        """
        init method for the super class
        """
        self.context = context
    
    def updatePrincipalMatrix(self, pMatrix, principal_id, settings):
        """ this method recursively populates the principal permissions
            dict  (MatrixDetails)
        """

        principals = zapi.principals()
        principal = principals.getPrincipal(principal_id)

        for setting in settings:
            for name, item in setting.items():
                self.updateMatrixRoles(pMatrix, principal_id, name,item)
                self.updateMatrixPermissions(pMatrix, principal_id, item)

    def updateMatrixPermissions(self, pMatrix, principal_id, item):
        """ Here we get all the permissions for the given principal
            on the item passed.
        """
            
        for prinPerms in item.get('principalPermissions', ()):
            if principal_id != prinPerms['principal']:
                continue

            # If this method is being used by permissionDetails then
            # we will have a read_perm in the self namespace. If it is
            # the same as curPerm we can continue
            curPerm = prinPerms['permission']
            if getattr(self,'read_perm',curPerm) != curPerm:
                continue
                
            if item.get('parentList',None):
                self.updatePermissionTree(pMatrix, item,prinPerms)

            mapping = {'permission': prinPerms['permission'],
                       'setting'   : prinPerms['setting'],}

            dup = [perm for perm in pMatrix['permissions'] \
                   if perm['permission'] == mapping['permission']]

            if dup:
                # This means we already have a record with this permission
                # and the next record would be less specific so we continue
                continue

            pMatrix['permissions'].append(mapping)

    def orderRoleTree(self,pMatrix):
        # This is silly I know but I want global settings at the end
        try:
            roleTree = pMatrix['roleTree']
            
            globalSettings = roleTree.pop(0)
            roleTree.append(globalSettings)
        except IndexError:
            # Attempting to pop empty list
            pass

    def updateRoleTree(self,pMatrix,item,parentList,curRole):
        """
        This method is responsible for poplating the roletree.
        """
        roleTree = pMatrix['roleTree']

        key = item.get('uid')
        keys =  [x.keys()[0] for x in roleTree]

        # Each key is unique so we just get the list index to edit
        if key in keys:
            listIdx = keys.index(key)
        else:
            roleTree.append({key:{}})
            listIdx = -1

        roleTree[listIdx][key]['parentList'] =  parentList
        roleTree[listIdx][key]['name'] = item.get('name')
        roleTree[listIdx][key].setdefault('roles',[])

        # We make sure we only add the roles we do not yet have.
        if curRole not in roleTree[listIdx][key]['roles']:
            roleTree[listIdx][key]['roles'].append(curRole)

    def updateRoles(self,pMatrix, item,role,curRole):
        if curRole['setting'] == Allow:
            # We only want to append the role if it is Allowed
            roles = pMatrix['roles']
            rolePerms = self.roleSettings['rolePermissions']

            if not roles.has_key(role):
                roles[role] = []

            # Here we get the permissions provided by each role
            for rolePerm in rolePerms:
                if rolePerm['role'] == role:
                    mapping = {'permission': rolePerm['permission'],
                               'setting'   : rolePerm['setting'].getName()
                              }

                    if mapping not in roles[role]:
                        roles[role].append(mapping)

    def updatePermissionTree(self,pMatrix, item,prinPerms):
        """ method responsible for creating permission tree """

        permissionTree = pMatrix['permissionTree']

        key = item.get('uid')
        keys =  [x.keys()[0] for x in permissionTree]

        # Each key is unique so we just get the list index to edit
        if key in keys:
            listIdx = keys.index(key)
        else:
            permissionTree.append({key:{}})
            listIdx = -1

        permissionTree[listIdx][key]['parentList'] = item.get('parentList')
        permissionTree[listIdx][key]['name'] = item.get('name')
        permissionTree[listIdx][key].setdefault('permissions',[])

        if prinPerms not in permissionTree[listIdx][key]['permissions']:
              permissionTree[listIdx][key]['permissions'].append(prinPerms)


class PermissionDetails(MatrixDetails):
    """Get permission details for a given principal and view.
    Includes the permissions set by the groups the principal belongs to.
    """

    implements(interfaces.IPermissionDetails)
    adapts(Interface)

    def __call__(self,principal_id,view_name, skin=IBrowserRequest):
        self.read_perm = 'zope.Public'
        self.view_name = view_name
        self.skin = skin

        request = TestRequest()
        applySkin(request, skin)
        pMatrix = {'permissions': [],
                   'permissionTree': [],
                   'roles': {},
                   'roleTree': [],
                   'groups': {}}

        ifaces = tuple(providedBy(self.context))

        for iface in ifaces:
            for view_reg in getViews(iface, skin):
                if  view_reg.name == view_name:

                    view = getView(self.context, view_reg, skin)
                    all_settings = [{name:val} for name,val in
                                     settingsForObject(view) ]

                    self.read_perm = \
                             getViewInfoDictionary(view_reg)['read_perm']\
                                or 'zope.Public'

                    self.roleSettings, junk = getSettingsForMatrix(view)
                    
                    self.rolePermMap = self.roleSettings.get(
                                              'rolePermissions', ())

                    self.updatePrincipalMatrix(pMatrix,
                                               principal_id,
                                               all_settings)
                    break

        principals = zapi.principals()
        principal = principals.getPrincipal(principal_id)

        if principal.groups:
            for group_id in principal.groups:
                gMatrix = {group_id: self(group_id,view_name,skin)}
                pMatrix['groups'].update(gMatrix)

            # The following section updates the principalPermissions with
            # the permissions found in the groups assigned. if the permisssion
            # already exists for the principal then we ignore it.
            permList = [x.items()[1][1] for x in pMatrix['permissions']]

            for matrix in gMatrix.values():
                for tmp in matrix['permissions']:
                    gPerm = tmp['permission']
                    if gPerm not in permList:
                        pMatrix['permissions'].append(tmp)

        self.orderRoleTree(pMatrix)
        return pMatrix

    def updateMatrixRoles(self, pMatrix, principal_id, name, item):
        """
        Updates the roles for the PermissionDetails class
        """
        for curRole in item.get('principalRoles', ()):
            if curRole['principal'] != principal_id:
                continue

            role = curRole['role']

            perm = roleProvidesPermission(self.rolePermMap,
                                          role,
                                          self.read_perm )

            if perm != 'Allow' and perm != 'Deny':
                continue

            parentList = item.get('parentList',None)

            if parentList:
                # If we have a parent list we want to populate the tree
                self.updateRoleTree(pMatrix, item,parentList,curRole)

            if curRole['setting'] == Deny:
                try:
                    # Here we see if we have added a security setting with
                    # this role before, if it is now denied we remove it.
                    del pMatrix['roles'][role]
                except:
                    #Cannot delete something that is not there
                    pass
            else:
                self.updateRoles(pMatrix, item,role,curRole)

class PrincipalDetails(MatrixDetails):
    implements(interfaces.IPrincipalDetails)
    adapts(Interface)

    def __call__(self,principal_id, skin=IBrowserRequest):
        """Return all security settings (permissions, groups, roles)
           for all interfaces provided by this context for a
           `principal_id`, and of course we are only after browser views"""

        request = TestRequest()
        applySkin(request, skin)
        pMatrix = {'permissions': [],
                   'permissionTree': [],
                   'roles': {},
                   'roleTree': [],
                   'groups': {}}

        ifaces = tuple(providedBy(self.context))

        for iface in ifaces:
            for view_reg in getViews(iface, IBrowserRequest):
                view = getView(self.context, view_reg, skin)
                if not view:
                    continue
                all_settings = [{name:val} for name,val in
                                 settingsForObject(view) ]

                self.roleSettings, junk = getSettingsForMatrix(view)
                self.updatePrincipalMatrix(pMatrix, principal_id, all_settings)

        principals = zapi.principals()
        principal = principals.getPrincipal(principal_id)

        if principal.groups:
            for group_id in principal.groups:
                gMatrix = {group_id: self(group_id)}
                pMatrix['groups'].update(gMatrix)
                
            # The following section updates the principalPermissions with
            # the permissions found in the groups assigned. if the permisssion
            # already exists for the principal then we ignore it.
            permList = [x.items()[1][1] for x in pMatrix['permissions']]
            for matrix in gMatrix.values():
                for tmp in matrix['permissions']:
                    gPerm = tmp['permission']
                    if gPerm not in permList:
                        pMatrix['permissions'].append(tmp)

        self.orderRoleTree(pMatrix)
        return pMatrix

    def updateMatrixRoles(self, pMatrix, principal_id, name, item):
        """
        updates the MatrixRoles for the PrincipalDetails class
        """
        for curRole in item.get('principalRoles', ()):
            if curRole['principal'] != principal_id:
                continue

            role = curRole['role']
            parentList = item.get('parentList',None)

            if parentList:
                # If we have a parent list we want to populate the tree
                self.updateRoleTree(pMatrix, item,parentList,curRole)

            if curRole['setting'] == Deny:
                try:
                    # Here we see if we have added a security setting with
                    # this role before, if it is now denied we remove it.
                    del pMatrix['roles'][role]
                except:
                    #Cannot delete something that is not there
                    pass
            else:
                self.updateRoles(pMatrix,item,role,curRole)

def getViews(iface, reqType=IRequest):
    """Get all view registrations for a particular interface."""
    gsm = getGlobalSiteManager()
    for reg in gsm.registeredAdapters():
        if (len(reg.required) == 2 and
            reg.required[1] is not None and
            reqType.isOrExtends(reg.required[1])):
            if (reg.required[0] is None or
                iface.isOrExtends(reg.required[0])):
                yield reg

# TODO: Not yet tested
def hasPermissionSetting(settings):
    """Check recursively if a security mapping contains any permission
    setting.
    """
    if (settings['permissions'] or settings['roles']):
        return True

    for setting in settings['groups'].values():
        if hasPermissionSetting(setting):
            return True

    return False

def principalDirectlyProvidesPermission(prinPermMap, principal_id,
                                        permission_id):
    """Return directly provided permission setting for a given principal and
    permission.
    """
    for prinPerm in prinPermMap:
        if (prinPerm['principal'] == principal_id and
            prinPerm['permission'] == permission_id):
            return prinPerm['setting'].getName()

def roleProvidesPermission(rolePermMap, role_id, permission_id):
    """Return the permission setting for a given role and permission."""

    for rolePerm in rolePermMap:
        if (rolePerm['role'] == role_id and
            rolePerm['permission'] == permission_id):
            return rolePerm['setting'].getName()

def principalRoleProvidesPermission(prinRoleMap, rolePermMap, principal_id,
                                    permission_id,role=None):
    """Return the role id and permission setting for a given principal and
    permission.
    """
    if role:
        for prinRole in prinRoleMap:
            if (prinRole['principal'] == principal_id and
                 prinRole['setting'].getName() == 'Allow' and
                 role == prinRole['role']):

                 role_id = prinRole['role']
                 return (role_id, roleProvidesPermission(rolePermMap, role_id,
                                                    permission_id))

    for prinRole in prinRoleMap:
        if (prinRole['principal'] == principal_id and
            prinRole['setting'].getName() == 'Allow'):
            role_id = prinRole['role']
            return (role_id, roleProvidesPermission(rolePermMap, role_id,
                                                    permission_id))
    return (None, None)

def renderedName(name):
    """The root folder is the only unlocated context object."""
    if name is None:
        return u'Root Folder'
    return name

def settingsForObject(ob):
    """Analysis tool to show all of the grants to a process
       This method was copied from zopepolicy.py in the zope.
       security policy package.  Also needed to add a parentList
       this just helps locate the object when we display it to the
       user.
    """
    result = []
    while ob is not None:

        data = {}
        principalPermissions = IPrincipalPermissionMap(ob, None)
        if principalPermissions is not None:
            settings = principalPermissions.getPrincipalsAndPermissions()
            #settings.sort() #The only difference from the original method
            data['principalPermissions'] = [
                {'principal': pr, 'permission': p, 'setting': s}
                for (p, pr, s) in settings]

        principalRoles = IPrincipalRoleMap(ob, None)
        if principalRoles is not None:
            settings = principalRoles.getPrincipalsAndRoles()
            data['principalRoles'] = [
                {'principal': p, 'role': r, 'setting': s}
                for (r, p, s) in settings]

        rolePermissions = IRolePermissionMap(ob, None)

        if rolePermissions is not None:
            settings = rolePermissions.getRolesAndPermissions()
            data['rolePermissions'] = [
                {'permission': p, 'role': r, 'setting': s}
                for (p, r, s) in settings]

        parent = getattr(ob, '__parent__', None)
        while parent is not None:
            if not data.has_key('parentList'):
                data['parentList'] = []
                thisName = getattr(ob, '__name__') or 'Root Folder'
                data['parentList'].append(thisName)

            if parent:
                name = getattr(parent, '__name__') or 'Root Folder'
                data['parentList'].append(name)

            parent = getattr(parent, '__parent__', None)

        result.append((getattr(ob, '__name__', '(no name)'), data))
        ob = getattr(ob, '__parent__', None)

        # This is just to create an internal unique name for the object
        # using the name and depth of the object. Im not sure but a
        # linkedlist may be a better approach.
        if data.has_key('parentList'):
            data['uid'] = data['parentList'][0]+"_" + \
                                str(len(data['parentList']))

    # Here we need to add the parentlist and uid to display it properly
    # in the roleTree and in the permissionTree
    result[-1][1]['parentList'] = ['Root Folder']
    result[-1][1]['uid']        = 'Root Folder'
    result[-1][1]['name']       = 'Root Folder'
    data = {}
    result.append(('global settings', data))

    settings = principalPermissionManager.getPrincipalsAndPermissions()
    settings.sort()
    data['principalPermissions'] = [
        {'principal': pr, 'permission': p, 'setting': s}
        for (p, pr, s) in settings]

    settings = principalRoleManager.getPrincipalsAndRoles()
    data['principalRoles'] = [
        {'principal': p, 'role': r, 'setting': s}
        for (r, p, s) in settings]

    settings = rolePermissionManager.getRolesAndPermissions()
    data['rolePermissions'] = [
        {'permission': p, 'role': r, 'setting': s}
        for (p, r, s) in settings]

    data['parentList'] = ['global settings']
    data['uid'] = 'global settings'

    return result

def getSettingsForMatrix(viewInstance):
    """ Here we aggregate all the principal permissions into one object
        We need them all for our lookups to work properly in
        principalRoleProvidesPermission.
    """
    allSettings = {}
    permSetting = ()
    settingList = [val for name ,val in settingsForObject(viewInstance)]

    # The settings list is an aggregate of all settings
    # so we can lookup permission settings for any role
    for setting in settingList:
        for key,val in setting.items():
            if not allSettings.has_key(key):
                allSettings[key] = []
            allSettings[key].extend(val)

    settings= settingsForObject(viewInstance)
    settings.reverse()

    return allSettings, settings

def getView(context, view_reg, skin=IBrowserRequest):
    """Instantiate view from given registration and skin.
       Return `None` if the view isn't callable.
    """
    request = TestRequest()
    applySkin(request, skin)
    try:
        view_inst = view_reg.factory(context, request)
        if callable(view_inst):
            return view_inst
    except TypeError:
        pass


def mergePermissionsFromGroups(principals,matrix):
    """
    This method recursively looks through all the principals in the
    viewPermMatrix and inspects the inherited permissions from groups
    assigned to the  principal.
    """
    # Actually this does need a post-order depth first...
    # Thanks Jacob
    sysPrincipals = zapi.principals()

    for principal in principals:
        for group_id in principal.groups:
            group = sysPrincipals.getPrincipal(group_id)
            mergePermissionsFromGroups([sysPrincipals.getPrincipal(x) for x in principal.groups],matrix)

            if matrix.has_key(group_id):
                res = matrix[group_id]
                for item in res:
                    # We only want the setting if we do not alread have it.
                    # or if it is an Allow permission as the allow seems to
                    # override the deny with conflicting group permissions.
                    if item not in matrix[principal.id] or res[item] == 'Allow':
                        matrix[principal.id][item] = res[item]

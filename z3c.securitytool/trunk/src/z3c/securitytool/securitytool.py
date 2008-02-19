from zope.interface import Interface, implements, providedBy
from zope.component import adapts, getMultiAdapter, getGlobalSiteManager
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import TestRequest, applySkin
from zope.publisher.interfaces import IRequest

from zope.app.apidoc.presentation import getViewInfoDictionary
from zope.i18nmessageid import ZopeMessageFactory as _
from zope.app.security.principalregistry import PrincipalRegistry

from zope.securitypolicy.interfaces import IPrincipalPermissionMap
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.securitypolicy.interfaces import IRolePermissionMap
from zope.securitypolicy.principalpermission import principalPermissionManager
from zope.securitypolicy.rolepermission import rolePermissionManager
from zope.securitypolicy.principalrole import principalRoleManager
from zope.securitypolicy.interfaces import Allow, Unset, Deny

from zope.securitypolicy.interfaces import IPrincipalPermissionManager, IPrincipalRoleManager
from zope.session.interfaces import ISession
from zope.app import zapi
from z3c.securitytool import interfaces

class SecurityChecker(object):
    """ Workhorse of the security tool package"""
    implements(interfaces.ISecurityChecker)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def getView(self, view_reg, skin=IBrowserRequest):
        """Instantiate view from given registration and skin.
           Return `None` if the view isn't callable.
        """
        request = TestRequest()
        applySkin(request, skin)
        try:
            view_inst = view_reg.factory(self.context, request)
            if callable(view_inst):
                return view_inst
        except TypeError:
            pass

    def getPermissionSettingsForAllViews(self,interfaces,skin=IBrowserRequest,
                                         selectedPermission=None):
        """ retrieves permission settings for all views"""
        request = TestRequest()
        self.skin = skin
        self.selectedPermission = selectedPermission

        applySkin(request, self.skin)

        self.viewMatrix = {}
        self.viewPermMatrix = {}
        self.viewRoleMatrix = {}
        self.views = {}
        self.permissions = set()

        for iface in interfaces:
            for view_reg in getViews(iface, self.skin):
                viewInstance = self.getView(view_reg, self.skin)
                if viewInstance:
                    self.populateMatrix(viewInstance,view_reg)

        # Two matricies are created a role matrix and a permission matrix.

        # The reason for the viewRoleMatrix is so lower roles in the tree
        # can overite higher roles. And the assigned permissions in roles
        # can be organized seperately than the assigned permissions to
        # objects.

        # Here we will merge the two matricies where the permission matrix
        # will always win

        for item in self.viewRoleMatrix:
            if not  self.viewMatrix.has_key(item):
                self.viewMatrix[item] = {}
            for viewSetting in self.viewRoleMatrix[item]:
                val = self.viewRoleMatrix[item][viewSetting] and 'Allow' or '--'
                self.viewMatrix[item].update({viewSetting:val})

        for item in self.viewPermMatrix:
            if not  self.viewMatrix.has_key(item):
                self.viewMatrix[item] = {}
            for viewSetting in self.viewPermMatrix[item]:
                self.viewMatrix[item].update(
                          {viewSetting:self.viewPermMatrix[item][viewSetting]})

        return [self.viewMatrix,self.views,self.permissions]

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

        allSettings, settings = self.getSettingsForMatrix(viewInstance)
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
                    try:
                        # Here we see if we have added a security setting with
                        # this role before, if it is now denied we remove it.
                        del self.viewRoleMatrix[principal]\
                                       [self.name][role['role']]
                    except KeyError:
                        pass
                    continue

                else:
                    permSetting= principalRoleProvidesPermission(
                                   principalRoles, rolePermMap,
                                   principal, read_perm,
                                   role['role']
                                )

                self.updateRolePermissionSetting(permSetting,principal,role)

            principalPermissions = allSettings.get('principalPermissions',[])
            self.populatePermissionMatrix(read_perm,principalPermissions)

    def updateRolePermissionSetting(self,permSetting,principal,role):
        """ Updates permission setting for current role if necessary"""
        if permSetting[1]:
            if permSetting[1] != 'Deny':
                if not self.viewRoleMatrix[principal].has_key(self.name):
                    self.viewRoleMatrix[principal][self.name] = {}

                self.viewRoleMatrix[principal][self.name].update(
                    {role['role']:permSetting[1]})


    def getSettingsForMatrix(self,viewInstance):
        """ Here we aggregate all the principal permissions into one object
            We need them all for our lookups to work properly in
            principalRoleProvidesPermission.
        """
        allSettings = {}
        permSetting = ()
        settingList = [val for name ,val  in settingsForObject(viewInstance)]

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


    def populatePermissionMatrix(self,read_perm,principalPermissions):
        """ This method populates the principal permission section of
            the view matrix
        """
        for principalPermission in principalPermissions:
            if principalPermission['permission'] == read_perm:
                principal = principalPermission['principal']
                permSetting = principalPermission['setting'].getName()
                if self.viewPermMatrix.has_key(principal):
                    if self.viewPermMatrix[principal].has_key(self.name):
                        if self.viewPermMatrix[principal][self.name] != 'Deny':
                            self.viewPermMatrix[principal].update(
                                {self.name: permSetting}
                                )
                    else:
                        self.viewPermMatrix[principal][self.name] = permSetting
                else:
                    self.viewPermMatrix[principal] = {self.name: permSetting}

    def principalPermissions(self, principal_id, skin=IBrowserRequest):
        """Return all security settings (permissions, groups, roles)
           for all interfaces provided by this context for a
           `principal_id`, and of course we are only after browser views"""

        request = TestRequest()
        applySkin(request, skin)
        self.principalMatrix = {'permissions': [],
                                'permissionTree': [],
                                'roles': {},
                                'roleTree': [],
                                'groups': {}}

        self.principals = zapi.principals()
        self.principal = self.principals.getPrincipal(principal_id)
        ifaces = tuple(providedBy(self.context))

        for iface in ifaces:
            for view_reg in getViews(iface, IBrowserRequest):
                view = self.getView(view_reg, skin)
                if not view:
                    continue
                all_settings = [{name:val} for name,val in
                                 settingsForObject(view) ]

                self.roleSettings, junk = \
                              self.getSettingsForMatrix(view)

                self.populatePrincipalMatrix(all_settings)

        self.orderRoleTree()
        return self.principalMatrix

    def orderRoleTree(self):
        # This is silly I know but I want global settings at the end
        try:
            globalSettings = self.principalMatrix['roleTree'].pop(0)
            self.principalMatrix['roleTree'].append(globalSettings)
        except IndexError:
            # Attempting to pop empty list
            pass

    def populatePrincipalMatrix(self, settings):
        """ this method recursively populates the principal permissions
            dict and is only used by principalPermissions """

        for setting in settings:
            for name, item in setting.items():
                self.populatePrincipalMatrixRoles(name,item)
                self.populatePrincipalMatrixPermissions(item)
            for group_id in self.principal.groups:
                group = self.principals.getPrincipal(group_id)
                self.principalMatrix['groups'][group_id] = \
                    self.policyPermissions(group, settings)


    def populatePrincipalMatrixRoles(self, name, item):
        for curRole in item.get('principalRoles', ()):
            if curRole['principal'] != self.principal.id:
                continue

            role = curRole['role']
            parentList = item.get('parentList',None)

            if parentList:
                # If we have a parent list we want to populate the tree
                self.populatePrincipalRoleTree(item,parentList,curRole)

            if curRole['setting'] == Deny:
                try:
                    # Here we see if we have added a security setting with
                    # this role before, if it is now denied we remove it.
                    del self.principalMatrix['roles'][role]
                except KeyError:
                    pass
                continue

            else:
                self.populatePrincipalRoles(item,role,curRole)

    def populatePrincipalRoleTree(self,item,parentList,curRole):
        key = item.get('uid')
        keys =  [x.keys()[0] for x in\
                 self.principalMatrix['roleTree']]

        if key not in keys:
            self.principalMatrix['roleTree'].append({
                                         key:{}})
            place = -1
        else:
            place = keys.index(key)

        # Each key is unique so we just get the list index to edit
        # we keep it as a list so the order stays the same.

        self.principalMatrix['roleTree'][place]\
             [key]['parentList'] = \
             parentList

        self.principalMatrix['roleTree'][place]\
             [key]['name'] = item.get('name')

        self.principalMatrix['roleTree']\
                        [place][key].setdefault('roles',[])


        # we make sure we only add the roles we do not yet have.
        if curRole not in \
                 self.principalMatrix['roleTree'][place]\
                           [key]['roles']:
            self.principalMatrix['roleTree'][place]\
                           [key]['roles'].append(curRole)

    def populatePrincipalRoles(self,item,role,curRole):
        if curRole['setting'] == Allow:
            # We only want to append the role if it is Allowed
            if not self.principalMatrix['roles'].has_key(role):
                self.principalMatrix['roles'][role] = []


            # Here we get the permissions provided by each role
            for rolePerm in self.roleSettings['rolePermissions']:
                if rolePerm['role'] == role:
                    permission = rolePerm['permission']
                    _setting = rolePerm['setting'].getName()
                    mapping = {'permission': permission,
                           'setting': _setting}
                    if mapping not in self.principalMatrix['roles'][role]:
                        self.principalMatrix['roles'][role].append(mapping)

    def populatePrincipalMatrixPermissions(self, item):
        # Here we get all the permssions for this principal

        for prinPerms in item.get('principalPermissions', ()):

            if self.principal.id != prinPerms['principal']:
                continue

            parentList = item.get('parentList',None)
            setting = prinPerms['setting'].getName()

            if parentList:
                self.populatePrincipalPermTree(item,parentList,prinPerms)

            permission = prinPerms['permission']
            _setting = prinPerms['setting']
            mapping = {'permission': permission,
                       'setting': _setting}

            dup = [x for x in self.principalMatrix['permissions'] \
                   if x['permission'] == permission] 

            if dup:
                # This means we already have a record with this permission
                # and the next record would be less specific so we continue
                continue

            self.principalMatrix['permissions'].append(mapping)


    def populatePrincipalPermTree(self,item,parentList,prinPerms):
        """ method responsible for creating permission tree """
        key = item.get('uid')
        keys =  [x.keys()[0] for x in\
                 self.principalMatrix['permissionTree']]

        if key not in keys:
            self.principalMatrix['permissionTree'].append({
                                         key:{}})
            place = -1
        else:
            place = keys.index(key)

        # Each key is unique so we just get the list index to edit
        # we keep it as a list so the order stays the same.

        self.principalMatrix['permissionTree'][place]\
             [key]['parentList'] = \
             parentList

        self.principalMatrix['permissionTree'][place]\
             [key]['name'] = item.get('name')

        self.principalMatrix['permissionTree']\
                        [place][key].setdefault('permissions',[])
        
        if prinPerms not in self.principalMatrix['permissionTree']\
           [place][key]['permissions']:
              self.principalMatrix['permissionTree']\
                  [place][key]['permissions'].append(prinPerms)


    def permissionDetails(self, principal_id, view_name, skin=IBrowserRequest):
        """Get permission details for a given principal and view.
        Includes the permissions set by the groups the principal belongs to.
        """
        principals = zapi.principals()
        principal = principals.getPrincipal(principal_id)

        read_perm = settings = None
        ifaces = tuple(providedBy(self.context))
        for iface in ifaces:
            for view_reg in getViews(iface, skin):
                if view_reg.name == view_name:

                    view = self.getView(view_reg, skin)
                    settings = settingsForObject(view)
                    read_perm = getViewInfoDictionary(view_reg)['read_perm']
                    break

        # Here we want to aggregate all the rolePermissions in one place
        rolePermissions = []
        if not settings:
            return  {'read_perm':'zope.Public',
                     'permissions': [],
                     'roles': [],
                     'groups': {}}

        if read_perm is None:
            prinPermSettings = {'permissions': [],
                                'roles': [],
                                'groups': {}}
            read_perm ='zope.Public'
        else:
            for name,setting in settings:
                if setting.get('rolePermissions',''):
                    rolePermissions.extend(setting['rolePermissions'])

            prinPermSettings = self._permissionDetails(principal,
                                                       read_perm,
                                                       settings,
                                                       rolePermissions)

        prinPermSettings['read_perm'] = read_perm

        return prinPermSettings

    def _permissionDetails(self,principal,read_perm,settings, rolePermissions):
        """Recursively get the permission details for a given principal and
        permission from a security mapping.
        """
        principalSettings = {'permissions': [],
                             'roles': {},
                             'groups': {}}
        principals = zapi.principals()

        for name, setting in settings:
            prinPermMap = setting.get('principalPermissions', ())
            prinRoleMap = setting.get('principalRoles', ())
            rolePermMap = rolePermissions
            permSetting = principalDirectlyProvidesPermission(prinPermMap,
                principal.id, read_perm)
            if permSetting:
                principalSettings['permissions'].append(
                    {'name': renderedName(name), 'setting': permSetting})

            role_id, permSetting = principalRoleProvidesPermission(
                prinRoleMap, rolePermMap, principal.id,read_perm )
            if permSetting:
                nameList = principalSettings['roles'].setdefault(role_id, [])
                nameList.append({'name': renderedName(name),
                                 'setting': permSetting})

            for group_id in principal.groups:
                group = principals.getPrincipal(group_id)
                group_settings = self._permissionDetails(group,
                    read_perm, settings, rolePermMap)

                if hasPermissionSetting(group_settings):
                    principalSettings['groups'][group_id] = group_settings

        return principalSettings


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
        # using the name and depth of the object.
        if data.has_key('parentList'):
            data['uid'] = data['parentList'][0]+"_" + \
                                str(len(data['parentList']))

    # Here we need to add the parentlist and uid to display it properly
    # in the roleTree and in the permissionTree
    result[-1][1]['parentList'] = ['Root Folder']
    result[-1][1]['uid'] = 'Root Folder'
    result[-1][1]['name'] = 'Root Folder'

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


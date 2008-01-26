from zope.interface import Interface, implements, providedBy
from zope.component import adapts, getMultiAdapter, getGlobalSiteManager
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import TestRequest, applySkin
from zope.publisher.interfaces import IRequest

from zope.app.apidoc.presentation import getViewInfoDictionary
from zope.i18nmessageid import ZopeMessageFactory as _
from zope.app.security.principalregistry import PrincipalRegistry

# The following imports are just so we can have the Duplicate
# settingsForObject without the sort call on settings
from zope.securitypolicy.interfaces import IPrincipalPermissionMap
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.securitypolicy.interfaces import IRolePermissionMap
from zope.securitypolicy.principalpermission import principalPermissionManager
from zope.securitypolicy.rolepermission import rolePermissionManager
from zope.securitypolicy.principalrole import principalRoleManager

#from zope.app.securitypolicy.zopepolicy import settingsForObject

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
        self.views = {}
        self.permissions = set()
        #import pdb; pdb.set_trace()
        for iface in interfaces:
            for view_reg in getViews(iface, self.skin):
                viewInstance = self.getView(view_reg, self.skin)
                if viewInstance:
                    self.populateMatrix(viewInstance,view_reg)
        return [self.viewMatrix,self.views,self.permissions]


    def populateMatrix(self,viewInstance,view_reg):
        """ populates the matrix used for display on all the views"""

        info = getViewInfoDictionary(view_reg)
        read_perm = info['read_perm']
        self.permissions.add(read_perm)
        if read_perm == None:
            read_perm = 'zope.Public'
        if self.selectedPermission and self.selectedPermission != read_perm:
            return 
        self.name = info['name']
        self.views[self.name] = read_perm

        settings = [entry[1] for entry in settingsForObject(viewInstance)]

        for setting in settings:
            rolePermMap = setting.get('rolePermissions', ())
            principalRoles = setting.get('principalRoles', [])
            for role in principalRoles:
                principal = role['principal']
                if read_perm == 'zope.Public':
                    permSetting = (role,'Allow')
                else:
                    permSetting= principalRoleProvidesPermission(
                                   principalRoles, rolePermMap, 
                                   principal, read_perm
                                )
                if permSetting[1]:
                    if self.viewMatrix.has_key(principal):
                        if self.viewMatrix[principal].has_key(self.name):
                            if self.viewMatrix[principal][self.name]!='Deny':
                                self.viewMatrix[principal].update(
                                 {self.name: permSetting[1]}
                                )
                        else:
                            self.viewMatrix[principal][self.name] =\
                                                   permSetting[1]
                    else:
                        self.viewMatrix[principal]={self.name: permSetting[1]} 

            principalPermissions =  setting.get('principalPermissions',[])
            self.populatePermissionMatrix(read_perm,principalPermissions)


    def populatePermissionMatrix(self,read_perm,principalPermissions):
        """ This method populates the principal permission section of
            the view matrix
        """
        for principalPermission in principalPermissions:
            if principalPermission['permission'] == read_perm:
                principal = principalPermission['principal']
                permSetting = principalPermission['setting'].getName()
                if self.viewMatrix.has_key(principal):
                    if self.viewMatrix[principal].has_key(self.name):
                        if self.viewMatrix[principal][self.name] != 'Deny':
                            self.viewMatrix[principal].update(
                                {self.name: permSetting}
                                )
                    else:
                        self.viewMatrix[principal][self.name] = permSetting
                else:
                    self.viewMatrix[principal] = {self.name: permSetting}

    
    def principalPermissions(self, principal_id, skin=IBrowserRequest):
        """Return all security settings for a `principal_id`."""

        request = TestRequest()
        applySkin(request, skin)

        principals = zapi.principals()
        principal = principals.getPrincipal(principal_id)

        ifaces = tuple(providedBy(self.context))
        for iface in ifaces:
            for view_reg in getViews(iface, IBrowserRequest):
                view = self.getView(view_reg, skin)
                if not view:
                    continue
                all_settings = [ settings[1] for settings in
                                 settingsForObject(view) ]
                prinPermSettings = self.policyPermissions(principal,
                                                          all_settings)

        return prinPermSettings




# TODO: Rename
    def policyPermissions(self, principal, settings):
        """ this method  populates the principal permissions dict """
        prinPermSettings = {'permissions': [],
                            'roles': {},
                            'groups': {}}
        principals = zapi.principals()
        for setting in settings:
            for prinPerms in setting.get('principalPermissions', ()):
                if prinPerms['principal'] == principal.id:
                    permission = prinPerms['permission']
                    _setting = prinPerms['setting'].getName()
                    mapping = {'permission': permission,
                               'setting': _setting}
                    if not mapping in prinPermSettings['permissions']:
                        prinPermSettings['permissions'].append(mapping)
            for prinRoles in setting.get('principalRoles', ()):
                if prinRoles['principal'] != principal.id:
                    continue
                role = prinRoles['role']
                for rolePerms in setting['rolePermissions']:
                    if rolePerms['role'] == role:
                        permission = rolePerms['permission']
                        _setting = rolePerms['setting'].getName()
                        mapping = {'permission': permission,
                                   'setting': _setting}
                        perms = prinPermSettings['roles'].setdefault(
                            role, [])
                        if not mapping in perms:
                            perms.append(mapping)
            for group_id in principal.groups:
                group = principals.getPrincipal(group_id)
                prinPermSettings['groups'][group_id] = \
                    self.policyPermissions(group, settings)
        return prinPermSettings




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

        if read_perm is None:
            prinPermSettings = {'permissions': [],'roles': {},'groups': {}}
            read_perm ='zope.Public'
        else:        
            prinPermSettings = self._permissionDetails(principal, read_perm,
                                                       settings)

        prinPermSettings['read_perm'] = read_perm

        return prinPermSettings

    def _permissionDetails(self, principal, read_perm, settings):
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
            rolePermMap = setting.get('rolePermissions', ())
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
                    read_perm, settings)

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
                                    permission_id):
    """Return the role id and permission setting for a given principal and
    permission.
    """
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
       security policy package. This method was copied becuase
       sort is a protected method and unavailable when traversing
       to the` __parent__` objects.
    """
    result = []
    while ob is not None:

        data = {}
        result.append((getattr(ob, '__name__', '(no name)'), data))
        
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
                
        ob = getattr(ob, '__parent__', None)

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

    return result


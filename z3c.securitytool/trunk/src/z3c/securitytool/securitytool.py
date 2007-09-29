from zope.interface import Interface, implements, providedBy
from zope.component import adapts, getMultiAdapter, getGlobalSiteManager
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import TestRequest, applySkin
from zope.publisher.interfaces import IRequest

from zope.app.apidoc.presentation import getViewInfoDictionary
from zope.app.i18n import ZopeMessageFactory as _
from zope.app.security.principalregistry import PrincipalRegistry
from zope.app.securitypolicy.zopepolicy import settingsForObject
from zope.app.session.interfaces import ISession
from zope.app import zapi

from z3c.securitytool import interfaces

class SecurityChecker(object):
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
        import pdb; pdb.set_trace()
        request = TestRequest()
        applySkin(request, skin)
        viewMatrix = {}
        views = {}
        permissions = set()
        for iface in interfaces:
            for view_reg in getViews(iface, skin):
                viewInstance = self.getView(view_reg, skin)
                if viewInstance:
                    info = getViewInfoDictionary(view_reg)
                    read_perm = info['read_perm']
                    permissions.add(read_perm)
                    if read_perm == None:
                        read_perm = 'zope.Public'
                    if selectedPermission and selectedPermission != read_perm:
                        continue
                    name = info['name']
                    views[name] = read_perm
                    settings = [entry[1] for entry in \
                                    settingsForObject(viewInstance)]
                    for setting in settings:
                        rolePermMap = setting.get('rolePermissions', ())
                        principalRoles = setting.get('principalRoles', [])
                        for role in principalRoles:
                            principal = role['principal']
                            if read_perm == 'zope.Public':
                                permissionSetting = (role,'Allow')
                            else:
                                permissionSetting=principalRoleProvidesPermission(
                                                        principalRoles, rolePermMap, 
                                                        principal, read_perm)
                            if permissionSetting[1]:
                                if viewMatrix.has_key(principal):
                                    if viewMatrix[principal].has_key(name):
                                        if viewMatrix[principal][name] != 'Deny':
                                            viewMatrix[principal].update(
                                                 {name: permissionSetting[1]}
                                                            )
                                    else:
                                        viewMatrix[principal][name] = permissionSetting[1]
                                else:
                                    viewMatrix[principal] = {name: permissionSetting[1]} 

                        principalPermissions = setting.get('principalPermissions',[])
                        for principalPermission in principalPermissions:
                            if principalPermission['permission'] == read_perm:
                                principal = principalPermission['principal']
                                permissionSetting = principalPermission['setting'].getName()
                                if viewMatrix.has_key(principal):
                                    if viewMatrix[principal].has_key(name):
                                        if viewMatrix[principal][name] != 'Deny':
                                            viewMatrix[principal].update(
                                                            {name: permissionSetting}
                                                            )
                                    else:
                                        viewMatrix[principal][name] = permissionSetting
                                else:
                                    viewMatrix[principal] = {name: permissionSetting}
        return [viewMatrix,views,permissions]

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


def getViews(iface, type=IRequest):
    """Get all view registrations for a particular interface."""
    gsm = getGlobalSiteManager()
    for reg in gsm.registeredAdapters():
        if (len(reg.required) == 2 and
            reg.required[1] is not None and
            type.isOrExtends(reg.required[1])):
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

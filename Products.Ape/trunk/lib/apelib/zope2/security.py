##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Zope 2 security information serializers.

$Id$
"""

from types import TupleType

from Persistence import PersistentMapping
from AccessControl.User import User, UserFolder
from AccessControl.Permission import pname
import Products

from apelib.core.interfaces import ISerializer
from apelib.core.schemas import RowSequenceSchema


_permission_dict_cache = None

def get_permission_dict():
    """Returns a dictionary mapping permission attribute name to permission.

    Does not discover permissions defined in ZClass products, since that
    would require access to the Zope application in the database.
    """
    global _permission_dict_cache
    if _permission_dict_cache is not None:
        return _permission_dict_cache
    res = {}
    for item in Products.__ac_permissions__:
        p = item[0]
        attr = pname(p)
        res[attr] = p
    _permission_dict_cache = res
    return res


## Declaration types:
##
## executable owner
##   "executable-owner", "", "", path/to/userfolder/username
## local roles
##   "local-role", role_name, "", username
## user-defined roles
##   "define-role", role_name, "", ""
## proxy roles
##   "proxy-role", role_name, "", ""
## permission mapping
##   "permission-role", role_name, permission_name, ""
##   "permission-no-acquire", "", permission_name, ""



class SecurityAttributes:
    """Zope 2 security attribute serializer."""

    __implements__ = ISerializer

    schema = RowSequenceSchema()
    schema.add('declaration_type', 'string')
    schema.add('role', 'string')
    schema.add('permission', 'string')
    schema.add('username', 'string')

    def can_serialize(self, obj):
        return 1

    def serialize(self, event):
        res = []

        # Get security attributes from the instance only, not the class.
        # There's no need to serialize the class attributes.
        obj_d = event.obj.__dict__
        eo = obj_d.get('_owner')
        if eo is not None:
            event.ignore('_owner')
            path, username = eo
            if '/' in username:
                raise ValueError, '/ not allowed in user names'
            s = '%s/%s' % ('/'.join(path), username)
            res.append(('executable-owner', '', '', s))

        roles = obj_d.get('__ac_roles__')
        if roles is not None:
            event.ignore('__ac_roles__')
            roles = list(roles)
            roles.sort()
            class_roles = getattr(event.obj.__class__, '__ac_roles__', None)
            if class_roles:
                class_roles = list(class_roles)
                class_roles.sort()
            if roles != class_roles:
                for role in roles:
                    res.append(('define-role', role, '', ''))
            # else inherit roles from the class

        local_roles = obj_d.get('__ac_local_roles__')
        if local_roles is not None:
            event.ignore('__ac_local_roles__')
            for username, roles in local_roles.items():
                for role in roles:
                    res.append(('local-role', role, '', username))

        proxy_roles = obj_d.get('_proxy_roles')
        if proxy_roles is not None:
            event.ignore('_proxy_roles')
            for role in proxy_roles:
                res.append(('proxy-role', role, '', ''))

        p_dict = None
        for attr, value in obj_d.items():
            if attr.endswith('_Permission') and attr.startswith('_'):
                if p_dict is None:
                    p_dict = get_permission_dict()
                p = p_dict.get(attr)
                if p is not None:
                    event.ignore(attr)
                    for role in value:
                        res.append(('permission-role', role, p, ''))
                    # List means acquired, tuple means not acquired.
                    if isinstance(value, TupleType):
                        res.append(('permission-no-acquire', '', p, ''))

        return res
        

    def deserialize(self, event, state):
        local_roles = {}       # { username -> [role,] }
        defined_roles = []     # [role,]
        proxy_roles = []       # [role,]
        permission_roles = {}  # { permission -> [role,] }
        permission_acquired = {}  # { permission -> 0 or 1 }

        obj = event.obj
        for decl_type, role, permission, username in state:
            if decl_type == 'executable-owner':
                assert not role
                assert not permission
                #assert username
                pos = username.rfind('/')
                if pos < 0:
                    # Default to the root folder
                    ufolder = ['acl_users']
                    uname = username
                else:
                    ufolder = list(username[:pos].split('/'))
                    uname = username[pos + 1:]
                assert ufolder
                assert uname
                obj._owner = (ufolder, uname)

            elif decl_type == 'local-role':
                #assert role
                assert not permission
                #assert username
                r = local_roles.get(username)
                if r is None:
                    r = []
                    local_roles[username] = r
                r.append(role)

            elif decl_type == 'define-role':
                #assert role
                assert not permission
                assert not username
                defined_roles.append(role)

            elif decl_type == 'proxy-role':
                #assert role
                assert not permission
                assert not username
                proxy_roles.append(role)

            elif decl_type == 'permission-role':
                #assert role
                #assert permission
                assert not username
                r = permission_roles.get(permission)
                if r is None:
                    r = []
                    permission_roles[permission] = r
                r.append(role)
                if not permission_acquired.has_key(permission):
                    permission_acquired[permission] = 1

            elif decl_type == 'permission-no-acquire':
                assert not role
                #assert permission
                assert not username
                permission_acquired[permission] = 0

            else:
                raise ValueError, (
                    'declaration_type %s unknown' % repr(decl_type))

        if local_roles:
            obj.__ac_local_roles__ = local_roles
        if defined_roles:
            defined_roles.sort()
            obj.__ac_roles__ = tuple(defined_roles)
        if proxy_roles:
            obj._proxy_roles = tuple(proxy_roles)
        
        for p, acquired in permission_acquired.items():
            roles = permission_roles.get(p, [])
            if not acquired:
                roles = tuple(roles)
            setattr(obj, pname(p), roles)



class UserFolderSerializer:
    """Serializer for a user folder.

    This version lets the application keep a list of all users in RAM.
    """

    __implements__ = ISerializer

    schema = RowSequenceSchema()
    schema.add('id', 'string', 1)
    schema.add('password', 'string')
    schema.add('roles', 'string:list')
    schema.add('domains', 'string:list')

    def can_serialize(self, obj):
        return isinstance(obj, UserFolder)

    def serialize(self, event):
        obj = event.obj
        assert isinstance(obj, UserFolder), repr(obj)
        state = []
        event.ignore('data')
        for id, user in obj.data.items():
            assert isinstance(user, User), repr(user)
            assert len(user.__dict__.keys()) == 4, user.__dict__.keys()
            r = list(user.roles)
            r.sort()
            d = list(user.domains)
            d.sort()
            state.append((id, user.__, tuple(r), tuple(d)))
            event.serialized(id, user, 0)
        event.upos.append(obj.data)
        event.upos.extend(obj.data.values())
        return state

    def deserialize(self, event, state):
        obj = event.obj
        assert isinstance(obj, UserFolder)
        obj.data = PersistentMapping()
        for id, password, roles, domains in state:
            user = User(id, password, roles, domains)
            obj.data[id] = user
            event.deserialized(id, user)
        event.upos.append(obj.data)
        event.upos.extend(obj.data.values())


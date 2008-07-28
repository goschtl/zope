# coding=utf-8
""" Hierarchical Roles - basic classes and functions """

from zope.interface import implements
from zope.component import getUtilitiesFor, getUtility
from zope.securitypolicy.role import Role

from z3c.hroles.interfaces import IHRole

class HRole(Role):
    implements(IHRole)

    def __init__(self, id, title, description="", includes=None):
        self.includes = includes
        super(HRole, self).__init__(id, title, description)

def getIncludedRoles(context, id):
    """ Get matching hierarchical roles """
    roles = []
    role = getUtility(IHRole, id, context)
    roles.append(role)
    inc_roles = getattr(role, 'includes', None)
    if inc_roles:
        for inc_role in inc_roles:
            roles.extend(getIncludedRoles(context, inc_role))
    return roles

def getHRoles(context, prefix):
    """ Return all available HRoles with the given specific prefix """
    roles = getUtilitiesFor(IHRole, context)
    return [role for name, role in roles if role.id.startswith(prefix)]
    

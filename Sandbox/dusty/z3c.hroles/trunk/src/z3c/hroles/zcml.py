"""
Meta configuration of hierarchical roles
"""

from zope.configuration.fields import MessageID
from zope.component.zcml import utility

from z3c.hroles.interfaces import IHRole
from z3c.hroles import HRole

from zope.securitypolicy.metadirectives import IDefineRoleDirective

class IDefineHRoleDirective(IDefineRoleDirective):
    """Define a new hierarchical role."""

    includes = MessageID(
        title=u"Includes",
        description=u"Included Roles",
        required=False)


def defineHRole(_context, id, title, description='', includes=''):
    iroles = includes.split()
    role = HRole(id, title, description, iroles)
    utility(_context, IHRole, role, name=id)



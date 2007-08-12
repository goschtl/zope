# Allows to edit content.
MANAGECONTENT = 'tfws.website.ManageContent'
# Allows to edit site components.
MANAGESITE = 'tfws.website.ManageSite'
# Allows to manage all users.
MANAGEUSERS = 'tfws.website.ManageUsers'
# Allows to view site
VIEW = 'tfws.website.View'

ALL = [VIEW, MANAGECONTENT, MANAGEUSERS, MANAGESITE]

import zope.interface
import zope.component
from zope.security.interfaces import IParticipation
from zope.security.management import getSecurityPolicy
from zope.app.security.interfaces import IAuthentication

def permsForPrincipal(context, principal):
    """Return a list of permissions allowed for principal."""
    permission_bits = hasPermissions(ALL, context,
                                     principal)
    return [perm for perm, has in zip(ALL, permission_bits)
            if has]

class ProbeParticipation:
    """A stub participation for use in hasPermissions."""
    zope.interface.implements(IParticipation)
    def __init__(self, principal):
        self.principal = principal
        self.interaction = None


def hasPermissions(permissions, object, principal):
    """Test if the principal has access according to the security policy."""
    participation = ProbeParticipation(principal)
    interaction = getSecurityPolicy()(participation)
    return [interaction.checkPermission(permission, object)
            for permission in permissions]

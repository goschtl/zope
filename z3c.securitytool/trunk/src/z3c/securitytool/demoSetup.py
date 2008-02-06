import transaction

from zope.app.folder import Folder

from zope.app import zapi

from zope.app.appsetup.bootstrap import getInformationFromEvent
from zope.securitypolicy.interfaces import IPrincipalPermissionManager, IPrincipalRoleManager


class Participation:
    interaction = None
    
class CreateStructure(object):
    def __init__(self,event):
        db, connection, root, root_folder = getInformationFromEvent(event)
        # Lets get the root folder so we can assign some permissions to
        # specific contexts
        root=zapi.getRoot(root_folder)
        rootPermManager = IPrincipalPermissionManager(root)
        rootRoleManager = IPrincipalRoleManager(root)

        rootRoleManager.assignRoleToPrincipal('zope.Editor', 'zope.daniel')
        rootRoleManager.assignRoleToPrincipal('zope.Writer', 'zope.daniel')

        rootPermManager.denyPermissionToPrincipal('concord.ReadIssue','zope.daniel')
        rootPermManager.denyPermissionToPrincipal('concord.CreateIssue','zope.daniel')
        rootPermManager.denyPermissionToPrincipal('concord.CreateIssue','zope.stephan')
        rootPermManager.denyPermissionToPrincipal('concord.CreateIssue','zope.markus')
        rootPermManager.denyPermissionToPrincipal('concord.CreateIssue','zope.anybody')

        transaction.commit()


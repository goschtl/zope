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

        roleManager = IPrincipalRoleManager(root)
        roleManager.assignRoleToPrincipal('zope.Editor', 'zope.daniel')
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.daniel')

        permManager = IPrincipalPermissionManager(root)

        permManager.denyPermissionToPrincipal('concord.ReadIssue',
                                              'zope.daniel')

        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.daniel')

        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.stephan')

        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.markus')

        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.anybody')

        transaction.commit()


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
        if 'Folder1' not in root:
            root['Folder1'] = Folder()

        if 'Folder2' not in root['Folder1']:
            root['Folder1']['Folder2'] = Folder()
            
        if 'Folder3' not in root['Folder1']['Folder2']:
            root['Folder1']['Folder2']['Folder3'] = Folder()

        sysPrincipals = zapi.principals()
        principals = [x.id for x in sysPrincipals.getPrincipals('')]


        roleManager = IPrincipalRoleManager(root)
        permManager = IPrincipalPermissionManager(root)
        
        roleManager.assignRoleToPrincipal('zope.Editor', 'zope.daniel')
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.daniel')
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.stephan')

        for principal in principals:
            permManager.grantPermissionToPrincipal('concord.ReadIssue',
                                              principal)
            permManager.denyPermissionToPrincipal('concord.DeleteArticle',
                                              principal)
            permManager.denyPermissionToPrincipal('concord.CreateArticle',
                                              principal)


        roleManager = IPrincipalRoleManager(root['Folder1'])
        permManager = IPrincipalPermissionManager(root['Folder1'])

        roleManager.assignRoleToPrincipal('zope.Janitor', 'zope.markus')
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.daniel')

        for principal in principals:
            permManager.denyPermissionToPrincipal('concord.ReadIssue',
                                              principal)
            permManager.grantPermissionToPrincipal('concord.DeleteIssue',
                                              principal)
            permManager.grantPermissionToPrincipal('concord.CreateArticle',
                                              principal)



        roleManager = IPrincipalRoleManager(root['Folder1']['Folder2'])
        permManager = IPrincipalPermissionManager(root['Folder1']['Folder2'])

        roleManager.assignRoleToPrincipal('zope.Janitor', 'zope.markus')
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.daniel')


        permManager.denyPermissionToPrincipal('concord.CreateArticle',
                                              'zope.daniel')
        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.daniel')
        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.stephan')
        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.markus')
        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.anybody')

        roleManager = IPrincipalRoleManager(root['Folder1']['Folder2']['Folder3'])
        permManager = IPrincipalPermissionManager(root['Folder1']['Folder2']['Folder3'])

        
        roleManager.removeRoleFromPrincipal('zope.Writer','zope.daniel')
        roleManager.removeRoleFromPrincipal('zope.Janitor', 'zope.markus')

        transaction.commit()

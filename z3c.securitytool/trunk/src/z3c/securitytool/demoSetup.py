import transaction
from zope.app.folder import Folder
from zope.app import zapi
from zope.app.appsetup.bootstrap import getInformationFromEvent
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.securitypolicy.interfaces import IPrincipalRoleManager


class Participation:
    interaction = None
    
class CreateStructure(object):
    def __init__(self,event):
        """ This method gets called on IDatabaseOpenedEvent when running the
            Demo we add some seemingly random security permissions to the
            folder tree created below so users of the demo can see what
            security tool can display
        """
        db, connection, root, root_folder = getInformationFromEvent(event)
        # Lets get the root folder so we can assign some permissions to
        # specific contexts
        root=zapi.getRoot(root_folder)

        # If the following folders do not exist... lets create them
        if 'Folder1' not in root:
            root['Folder1'] = Folder()

        if 'Folder2' not in root['Folder1']:
            root['Folder1']['Folder2'] = Folder()
            
        if 'Folder3' not in root['Folder1']['Folder2']:
            root['Folder1']['Folder2']['Folder3'] = Folder()

        # Lets get the list of all principals on the system.
        sysPrincipals = zapi.principals()
        principals = [x.id for x in sysPrincipals.getPrincipals('')
                      if x.id not in ['group1','group2','randy']]

# Here is where we begin to set the permissions for the root context level
        roleManager = IPrincipalRoleManager(root)
        permManager = IPrincipalPermissionManager(root)
        roleManager.assignRoleToPrincipal('zope.Editor', 'zope.group1')

        # Here we assign the group group1 to zope.daniel and zope.randy

        group1  = sysPrincipals.getPrincipal('zope.group1')
        group2  = sysPrincipals.getPrincipal('zope.group2')
        daniel  = sysPrincipals.getPrincipal('zope.daniel')
        randy  = sysPrincipals.getPrincipal('zope.randy')


        daniel.groups.append('zope.group1')
        group1.groups.append('zope.group2')

        randy.groups.append('zope.group1')
        randy.groups.append('zope.group2')

        
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.daniel')
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.stephan')

        for principal in principals:
            permManager.grantPermissionToPrincipal('concord.ReadIssue',
                                              principal)
            permManager.denyPermissionToPrincipal('concord.DeleteArticle',
                                              principal)
            permManager.denyPermissionToPrincipal('concord.CreateArticle',
                                              principal)


# Here is where we begin to set the permissions for the context level of
# Folder1.
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

        permManager.denyPermissionToPrincipal('concord.DeleteIssue',
                                              group1.id)
        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              group1.id)

        permManager.grantPermissionToPrincipal('concord.DeleteIssue',
                                              group2.id)
        permManager.grantPermissionToPrincipal('concord.CreateIssue',
                                              group2.id)

# Here is where we begin to set the permissions for the context level of
# /root/Folder1/Folder2.
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

# Here is where we begin to set the permissions for the context level of
# /root/Folder1/Folder2/Folder3.
        roleManager = IPrincipalRoleManager(root['Folder1']\
                                                ['Folder2']\
                                                ['Folder3'])
        permManager = IPrincipalPermissionManager(root['Folder1']\
                                                      ['Folder2']\
                                                      ['Folder3'])

        
        roleManager.removeRoleFromPrincipal('zope.Writer','zope.daniel')
        roleManager.removeRoleFromPrincipal('zope.Janitor', 'zope.markus')

        transaction.commit()

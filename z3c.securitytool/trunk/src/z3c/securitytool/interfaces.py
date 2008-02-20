from zope.interface import Interface

class ISecurityChecker(Interface):

    def getPermissionSettingsForAllViews(self,interfaces,skin,selectedPermission=None):
        """ gets the permission settings for all views"""
    def aggregateMatrices(self):
        """ aggregates the two matricies together """
        
    def getReadPerm(self,view_reg):
        """ gets the read permission for the view """
        
    def populateMatrix(self,viewInstance,view_reg):
        """ workhorse of the SecurityChecker class """
        
    def updateRolePermissionSetting(self,permSetting,principal,role,name):
        """ updates the permission settings """
        
    def populatePermissionMatrix(self,read_perm,principalPermissions):
        """ populates the permission matrix """


class IPermissionDetails(Interface):
    def permissionDetails(principal,read_perm,settings, rolePermissions):
        """ workhorse of the PermissionDetails class """

class IPrincipalDetails(Interface):
    def principalPermissions(principal_id, skin):
        """ main workhorse of the class """
    def orderRoleTree(self):
        """ This is an ordering method for the roleTree """
        
    def updatePrincipalMatrix( settings):
        """ this is called to update the roles and permissions"""
        
    def updatePrincipalMatrixRoles( name, item):
        """ method to up date the matrix roles """
        
    def updateRoleTree(item,parentList,curRole):
        """ method to update the matrix roletree """

    def updateRoles(item,role,curRole):
        """ method to update the roles """
        
    def updatePrincipalMatrixPermissions( item):
        """ method to update the permissions """
        
    def updatePermissionTree(item,prinPerms):
        """ method to update the permission tree """


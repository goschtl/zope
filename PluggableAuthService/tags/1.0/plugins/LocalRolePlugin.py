""" Classes: LocalRolePlugin

$Id$
"""
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin

from Products.PluggableAuthService.permissions import ManageUsers

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin

manage_addLocalRolePluginForm = PageTemplateFile(
    'www/lrpAdd', globals(), __name__='manage_addLocalRolePluginForm' )

def addLocalRolePlugin( dispatcher, id, title='', RESPONSE=None ):
    """ Add a Local Role Plugin to 'dispatcher'.
    """

    lrp = LocalRolePlugin( id, title )
    dispatcher._setObject( id, lrp )

    if RESPONSE is not None:
        RESPONSE.redirect( '%s/manage_main?manage_tabs_message=%s' %
                           ( dispatcher.absolute_url()
                           , 'LocalRolePlugin+added.' ) )

class LocalRolePlugin( BasePlugin ):
    """ Provide roles during Authentication from local roles
        assignments made on the root object.
    """

    __implements__ = BasePlugin.__implements__ + ( IRolesPlugin, )
    
    meta_type = 'Local Role Plugin'
    security = ClassSecurityInfo()

    def __init__( self, id, title=None ):
        self._setId( id )
        self.title = title

    #
    #    IRolesPlugin implementation
    #
    security.declarePrivate( 'getRolesForPrincipal' )
    def getRolesForPrincipal( self, principal, request=None ):

        """ See IRolesPlugin.
        """
        local_roles = getattr( self.getPhysicalRoot()
                             , '__ac_local_roles__'
                             , None )
        if local_roles is None:
            return None
        return local_roles.get( principal.getId() )

InitializeClass( LocalRolePlugin )

    

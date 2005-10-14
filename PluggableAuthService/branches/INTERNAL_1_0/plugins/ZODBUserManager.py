""" Classes: ZODBUserManager

$Id$
"""
import sha

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager
from App.class_init import default__class_init__ as InitializeClass
from BTrees.OOBTree import OOBTree
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins \
    import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins \
    import IUserEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins \
    import IUserAdderPlugin

from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.permissions import SetOwnPassword

manage_addZODBUserManagerForm = PageTemplateFile(
    'www/zuAdd', globals(), __name__='manage_addZODBUserManagerForm' )

def addZODBUserManager( dispatcher, id, title=None, REQUEST=None ):
    """ Add a ZODBUserManagern to a Pluggable Auth Service. """

    zum = ZODBUserManager(id, title)
    dispatcher._setObject(zum.getId(), zum)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'ZODBUserManager+added.'
                            % dispatcher.absolute_url())

class ZODBUserManager( BasePlugin ):

    """ PAS plugin for managing users in the ZODB.
    """
    __implements__ = ( IAuthenticationPlugin
                     , IUserEnumerationPlugin
                     , IUserAdderPlugin
                     )

    meta_type = 'ZODB User Manager'

    security = ClassSecurityInfo()

    def __init__(self, id, title=None):

        self._id = self.id = id
        self.title = title

        self._user_passwords = OOBTree()
        self._login_to_userid = OOBTree()
        self._userid_to_login = OOBTree()

    #
    #   IAuthenticationPlugin implementation
    #
    security.declarePrivate( 'authenticateCredentials' )
    def authenticateCredentials( self, credentials ):

        """ See IAuthenticationPlugin.

        o We expect the credentials to be those returned by
          ILoginPasswordExtractionPlugin.
        """
        login = credentials.get( 'login' )
        password = credentials.get( 'password' )

        if login is None or password is None:
            return None

        userid = self._login_to_userid.get( login, login )
        digested = sha.sha( password ).hexdigest()
        
        if self._user_passwords.get( userid ) == digested:
            return userid, login

        return None

    #
    #   IUserEnumerationPlugin implementation
    #
    security.declarePrivate( 'enumerateUsers' )
    def enumerateUsers( self
                      , id=None
                      , login=None
                      , exact_match=False
                      , sort_by=None
                      , max_results=None
                      , **kw
                      ):

        """ See IUserEnumerationPlugin.
        """
        user_info = []
        user_ids = []
        plugin_id = self.getId()

        if isinstance( id, str ):
            id = [ id ]

        if isinstance( login, str ):
            login = [ login ]

        if exact_match and ( id or login ):

            if id:
                user_ids.extend( id )
            elif login:
                user_ids.extend( [ self._login_to_userid.get( x )
                                    for x in login ] )

        if user_ids:
            user_filter = None

        else:   # Searching
            user_ids = self.listUserIds()
            user_filter = _ZODBUserFilter( id, login, **kw )

        for user_id in user_ids:

            if self._userid_to_login.get( user_id ):
                e_url = '%s/manage_users' % self.getId()
                qs = 'user_id=%s' % user_id

                info = { 'id' : user_id
                       , 'login' : self._userid_to_login[ user_id ]
                       , 'pluginid' : plugin_id
                       , 'editurl' : '%s?%s' % (e_url, qs)
                       } 

                if not user_filter or user_filter( info ):
                    user_info.append( info )

        return tuple( user_info )

    #
    #   IUserAdderPlugin implementation
    #
    security.declarePrivate( 'doAddUser' )
    def doAddUser( self, login, password ):
        try:
            self.addUser( login, login, password )
        except KeyError:
            return False
        return True

    #
    #   (notional)IZODBUserManager interface
    #
    security.declareProtected( ManageUsers, 'listUserIds' )
    def listUserIds( self ):

        """ -> ( user_id_1, ... user_id_n )
        """
        return self._user_passwords.keys()

    security.declareProtected( ManageUsers, 'getUserInfo' )
    def getUserInfo( self, user_id ):

        """ user_id -> {}
        """
        return { 'user_id' : user_id
               , 'login_name' : self._userid_to_login[ user_id ]
               , 'pluginid' : self.getId()
               }

    security.declareProtected( ManageUsers, 'listUserInfo' )
    def listUserInfo( self ):

        """ -> ( {}, ...{} )

        o Return one mapping per user, with the following keys:

          - 'user_id' 
          - 'login_name'
        """
        return [ self.getUserInfo( x ) for x in self._user_passwords.keys() ]

    security.declareProtected( ManageUsers, 'getUserIdForLogin' )
    def getUserIdForLogin( self, login_name ):

        """ login_name -> user_id

        o Raise KeyError if no user exists for the login name.
        """
        return self._login_to_userid[ login_name ]

    security.declareProtected( ManageUsers, 'getLoginForUserId' )
    def getLoginForUserId( self, user_id ):

        """ user_id -> login_name

        o Raise KeyError if no user exists for that ID.
        """
        return self._userid_to_login[ user_id ]

    security.declarePrivate( 'addUser' )
    def addUser( self, user_id, login_name, password ):

        if self._user_passwords.get( user_id ) is not None:
            raise KeyError, 'Duplicate user ID: %s' % user_id

        if self._login_to_userid.get( login_name ) is not None:
            raise KeyError, 'Duplicate login name: %s' % login_name

        self._user_passwords[ user_id ] = sha.sha( password ).hexdigest()
        self._login_to_userid[ login_name ] = user_id
        self._userid_to_login[ user_id ] = login_name

    security.declarePrivate( 'removeUser' )
    def removeUser( self, user_id ):

        if self._user_passwords.get( user_id ) is None:
            raise KeyError, 'Invalid user ID: %s' % user_id

        login_name = self._userid_to_login[ user_id ]

        del self._user_passwords[ user_id ]
        del self._login_to_userid[ login_name ]
        del self._userid_to_login[ user_id ]

    security.declarePrivate( 'updateUserPassword' )
    def updateUserPassword( self, user_id, login_name, password ):

        if self._user_passwords.get( user_id ) is None:
            raise KeyError, 'Invalid user ID: %s' % user_id

        old_login_name = self._userid_to_login[ user_id ]

        if old_login_name != login_name:
            del self._login_to_userid[ old_login_name ]
            self._login_to_userid[ login_name ] = user_id
            self._userid_to_login[ user_id ] = login_name

        if password:
            digested = sha.sha( password ).hexdigest()
            self._user_passwords[ user_id ] = digested

    #
    #   ZMI
    #
    manage_options = ( ( { 'label': 'Users', 
                           'action': 'manage_users', }
                         ,
                       )
                     + BasePlugin.manage_options
                     )

    security.declarePublic( 'manage_widgets' )
    manage_widgets = PageTemplateFile( 'www/zuWidgets'
                                     , globals()
                                     , __name__='manage_widgets'
                                     )

    security.declareProtected( ManageUsers, 'manage_users' )
    manage_users = PageTemplateFile( 'www/zuUsers'
                                   , globals()
                                   , __name__='manage_users'
                                   )

    security.declareProtected( ManageUsers, 'manage_addUser' )
    def manage_addUser( self
                      , user_id
                      , login_name
                      , password
                      , confirm
                      , RESPONSE=None
                      ):
        """ Add a user via the ZMI.
        """
        if password != confirm:
            message = 'password+and+confirm+do+not+match'

        else:
        
            if not login_name:
                login_name = user_id

            # XXX:  validate 'user_id', 'login_name' against policies?

            self.addUser( user_id, login_name, password )

            message = 'User+added'

        if RESPONSE is not None:
            RESPONSE.redirect( '%s/manage_users?manage_tabs_message=%s'
                             % ( self.absolute_url(), message )
                             )

    security.declareProtected( ManageUsers, 'manage_updateUserPassword' )
    def manage_updateUserPassword( self
                                 , user_id
                                 , login_name
                                 , password
                                 , confirm
                                 , RESPONSE=None
                                 ):
        """ Update a user's login name / password via the ZMI.
        """
        if password and password != confirm:
            message = 'password+and+confirm+do+not+match'

        else:
        
            if not login_name:
                login_name = user_id

            # XXX:  validate 'user_id', 'login_name' against policies?

            self.updateUserPassword( user_id, login_name, password )

            message = 'password+updated'

        if RESPONSE is not None:
            RESPONSE.redirect( '%s/manage_users?manage_tabs_message=%s'
                             % ( self.absolute_url(), message )
                             )

    security.declareProtected( ManageUsers, 'manage_removeUsers' )
    def manage_removeUsers( self
                          , user_ids
                          , RESPONSE=None
                          ):
        """ Remove one or more users via the ZMI.
        """
        user_ids = filter( None, user_ids )

        if not user_ids:
            message = 'no+users+selected'

        else:
        
            for user_id in user_ids:
                self.removeUser( user_id )

            message = 'Users+removed'

        if RESPONSE is not None:
            RESPONSE.redirect( '%s/manage_users?manage_tabs_message=%s'
                             % ( self.absolute_url(), message )
                             )

    #
    #   Allow users to change their own login name and password.
    #
    security.declareProtected( SetOwnPassword, 'getOwnUserInfo' )
    def getOwnUserInfo( self ):

        """ Return current user's info.
        """
        user_id = getSecurityManager().getUser().getId()

        return self.getUserInfo( user_id )

    security.declareProtected( SetOwnPassword, 'manage_updatePasswordForm' )
    manage_updatePasswordForm = PageTemplateFile( 'www/zuPasswd'
                                   , globals()
                                   , __name__='manage_updatePasswordForm'
                                   )

    security.declareProtected( SetOwnPassword, 'manage_updatePassword' )
    def manage_updatePassword( self
                             , login_name
                             , password
                             , confirm
                             , RESPONSE=None
                             ):
        """ Update the current user's password and login name.
        """
        user_id = getSecurityManager().getUser().getId()
        if password != confirm:
            message = 'password+and+confirm+do+not+match'

        else:
        
            if not login_name:
                login_name = user_id

            # XXX:  validate 'user_id', 'login_name' against policies?

            self.updateUserPassword( user_id, login_name, password )

            message = 'password+updated'

        if RESPONSE is not None:
            RESPONSE.redirect( '%s/manage_updatePasswordForm'
                               '?manage_tabs_message=%s'
                             % ( self.absolute_url(), message )
                             )

InitializeClass( ZODBUserManager )

class _ZODBUserFilter:

    def __init__( self
                , id=None
                , login=None
                , **kw
                ):

        self._filter_ids = id
        self._filter_logins = login

    def __call__( self, user_info ):

        if self._filter_ids:

            key = 'id'
            to_test = self._filter_ids

        elif self._filter_logins:

            key = 'login'
            to_test = self._filter_logins

        else:
            return 1 # TODO:  try using 'kw'

        value = user_info.get( key )

        if not value:
            return 0

        for contained in to_test:
            if value.lower().find( contained.lower() ) >= 0:
                return 1

        return 0

##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import unittest

from Acquisition import Implicit, aq_base, aq_parent
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from OFS.ObjectManager import ObjectManager
from OFS.Folder import Folder
from zExceptions import Unauthorized, Redirect

from Products.PluggableAuthService.utils import directlyProvides

class DummyPlugin(Implicit):
    pass

class DummyUserEnumerator( DummyPlugin ):

    def __init__( self, user_id, login=None ):

        self._user_id = self.PLUGINID = user_id

        if login is None:
            login = user_id

        self._login = login

    def enumerateUsers( self, **kw ):

        result = [ { 'id' : self._user_id
                   , 'login' : self._login
                   , 'pluginid' : self.PLUGINID
                   } ]

        if kw.get( 'id' ) == self._user_id:
            return tuple(result)

        if kw.get( 'login' ) == self._login:
            return tuple(result)

        return ()

class DummyGroupEnumerator( DummyPlugin ):

    def __init__( self, group_id ):

        self._group_id = self.PLUGINID = group_id

    def enumerateGroups( self
                       , id=None
                       , exact_match=True
                       , sort_by=None
                       , max_results=None
                       , **kw
                       ):

        result = [ { 'id' : self._group_id
                   , 'pluginid' : self.PLUGINID
                   } ]

        if id:
            if self._group_id.find( id ) >= 0:
                return tuple(result)
        return ()

class DummySuperEnumerator(DummyUserEnumerator, DummyGroupEnumerator):

    PLUGINID = 'super'

    def __init__(self, user_id, login, group_id):
        self._user_id = user_id
        self._login = login
        self._group_id = group_id

class DummyGroupPlugin(DummyPlugin):

    def __init__(self, id, groups=()):

        self._id = id
        self._groups = groups

    def getGroupsForPrincipal(self, user, REQUEST=None):

        return self._groups

class DummyChallenger( DummyPlugin ):

    def __init__(self, id):
        self.id = id

    def challenge(self, request, response):
        # Mark on the faux response that we have seen it:
        response.challenger = self
        return True

class DummyBadChallenger( DummyChallenger ):

    def challenge(self, request, response):
        # We don't play here.
        return False

class DummyReindeerChallenger( DummyChallenger ):

    def challenge(self, request, response):
        reindeer_games = getattr(response, 'reindeer_games', [])
        reindeer_games.append(self.id)
        response.reindeer_games = reindeer_games
        return True

class DummyCounterChallenger( DummyChallenger ):

    def __init__(self, id):
        self.id = id
        self.count = 0

    def challenge(self, request, response):
        self.count += 1
        return True

class FauxRequest:

    def __init__( self, steps=(), **kw ):

        self.steps = steps
        self._dict = {}
        self._dict.update( kw )
        self._held = []

    def get( self, key, default=None ):

        return self._dict.get( key, default )

    def _authUserPW( self ):
        form = self.get( 'form' )
        return ( form.get( 'login' ), form.get( 'password' ) )

    def __getitem__( self, key ):

        return self._dict[ key ]

    def __setitem__( self, key, value ):

        self._dict[ key ] = value

    def _hold(self, something):
        self._held.append(something)

class FauxNotFoundError( Exception ):

    pass

class FauxResponse:

    def __init__( self ):
        pass

    def notFoundError( self, message ):
        raise FauxNotFoundError, message

    def _unauthorized(self):
        self.challenger = self

    def unauthorized(self):
        self._unauthorized()
        raise Unauthorized, 'You can not do this!'

    def exception(self):
        self._unauthorized()
        return "An error has occurred."

class FauxObject( Implicit ):

    def __init__( self, id=None ):

        self._id = id

    def getId( self ):

        return self._id

    def __repr__( self ):

        return '<FauxObject: %s>' % self._id

    def publishable( self, *args, **kw ):

        return 'Args: %s\nKeywords: %s' % ( args, kw )

    def this(self):
        return self

class FauxContainer( FauxObject, ObjectManager ):

    pass

class FauxRoot( FauxContainer ):

    isTopLevelPrincipiaApplicationObject = 1

    def getPhysicalRoot( self ):
        return self

    def getPhysicalPath( self ):
        return ()

class FauxUser( Implicit ):

    def __init__( self, id, name=None, roles={}, groups={} ):

        self._id = id
        self._name = name
        self._roles = roles
        self._groups = groups

    def getId( self ):

        return self._id

    def getUserName( self ):

        return self._name

    def getRoles( self ):

        return self._roles

    def getGroups(self):

        return self._groups.keys()

    def allowed( self, value, roles ):

        for role in roles:
            if role in self._roles:
                return 1

        return 0

    def _addGroups(self, groups):
        for group in groups:
            self._groups[group] = 1

    def _addRoles(self, roles):
        for role in roles:
            self._roles[role] = 1

    def __repr__( self ):

        return '<FauxUser: %s>' % self._id

def _extractLogin( request ):

    return { 'login' : request[ 'form' ].get( 'login' )
           , 'password' : request[ 'form' ].get( 'password' )
           }

def _authLogin( credentials ):

    return (credentials[ 'login' ], credentials[ 'login' ])


def _extractExtra( request ):

    return { 'user' : request.get( 'extra' )
           , 'salt' : 'pepper'
           }

def _authExtra( credentials ):

    return ( credentials.get( 'salt' ) == 'pepper'
         and (credentials[ 'user' ], credentials[ 'user' ]) or None )

class PluggableAuthServiceTests( unittest.TestCase ):

    _oldSecurityPolicy = None

    def tearDown( self ):

        if self._oldSecurityPolicy is not None:
            setSecurityPolicy( self._oldSecurityPolicy )

        noSecurityManager()

    def _getTargetClass( self ):

        from Products.PluggableAuthService.PluggableAuthService \
            import PluggableAuthService

        return PluggableAuthService

    def _makeOne( self, plugins=None, *args, **kw ):

        zcuf = self._getTargetClass()( *args, **kw )

        if plugins is not None:
            zcuf._setObject( 'plugins', plugins )

        return zcuf

    def _makePlugins( self, plugin_type_info=None ):

        from Products.PluggableAuthService.PluggableAuthService \
            import _PLUGIN_TYPE_INFO
        from Products.PluginRegistry.PluginRegistry import PluginRegistry

        if plugin_type_info is None:
            plugin_type_info = _PLUGIN_TYPE_INFO

        reg = PluginRegistry( plugin_type_info=plugin_type_info )
        reg._setId( 'plugins' )
        reg._plugins = {}

        return reg

    def _makeTree( self ):

        rc = FauxObject( 'rc' )
        root = FauxRoot( 'root' ).__of__( rc )
        folder = FauxContainer( 'folder' ).__of__( root )
        object = FauxObject( 'object' ).__of__( folder )

        return rc, root, folder, object

    def _makeUserEnumerator( self, user_id, login=None ):

        from Products.PluggableAuthService.interfaces.plugins \
             import IUserEnumerationPlugin

        enumerator = DummyUserEnumerator( user_id, login )
        directlyProvides( enumerator, ( IUserEnumerationPlugin, ) )

        return enumerator

    def _makeGroupEnumerator( self, group_id ):

        from Products.PluggableAuthService.interfaces.plugins \
             import IGroupEnumerationPlugin

        enumerator = DummyGroupEnumerator( group_id )
        directlyProvides( enumerator, ( IGroupEnumerationPlugin, ) )

        return enumerator

    def _makeSuperEnumerator( self, user_id, login, group_id ):

        from Products.PluggableAuthService.interfaces.plugins \
             import IUserEnumerationPlugin
        from Products.PluggableAuthService.interfaces.plugins \
             import IGroupEnumerationPlugin

        enumerator = DummySuperEnumerator( user_id, login, group_id )
        directlyProvides( enumerator, ( IUserEnumerationPlugin,
                                        IGroupEnumerationPlugin ) )

        return enumerator

    def _makeGroupPlugin(self, id, groups=()):
        from Products.PluggableAuthService.interfaces.plugins \
             import IGroupsPlugin

        gp = DummyGroupPlugin(id, groups=groups)
        directlyProvides( gp, (IGroupsPlugin,) )
        return gp

    def _makeChallengePlugin(self, id, klass):
        from Products.PluggableAuthService.interfaces.plugins \
             import IChallengePlugin

        cp = klass(id)
        directlyProvides( cp, (IChallengePlugin,) )
        return cp

    def test_conformance_IUserFolder( self ):

        from Products.PluggableAuthService.interfaces.authservice \
            import IUserFolder

        from Interface.Verify import verifyClass

        verifyClass( IUserFolder, self._getTargetClass() )

    def test_empty( self ):

        zcuf = self._makeOne()

        self.assertEqual( zcuf.getId(), 'acl_users' )

    def test_checkBeforeTraverse( self ):

        rc, root, folder, object = self._makeTree()

        zcuf = self._makeOne()

        root._setObject('acl_users', zcuf)

        self.assertEqual( len(root.__before_traverse__), 1)

    def test__extractUserIds_simple( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin, IAuthenticationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        login = DummyPlugin()
        directlyProvides( login, ( IExtractionPlugin, IAuthenticationPlugin ) )
        login.extractCredentials = _extractLogin
        login.authenticateCredentials = _authLogin
        zcuf._setObject( 'login', login )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IExtractionPlugin, 'login' )
        plugins.activatePlugin( IAuthenticationPlugin, 'login' )

        request = FauxRequest( form={ 'login' : 'foo', 'password' : 'bar' } )

        user_ids = zcuf._extractUserIds( request=request
                                       , plugins=zcuf.plugins
                                       )

        self.assertEqual( len( user_ids ), 1 )
        self.assertEqual( user_ids[ 0 ][0], 'login__foo' )

    def test__extractUserIds_one_extractor_two_authenticators( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin, IAuthenticationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        login = DummyPlugin()
        directlyProvides( login, ( IExtractionPlugin, IAuthenticationPlugin ) )
        login.extractCredentials = _extractLogin
        login.authenticateCredentials = _authLogin

        zcuf._setObject( 'login', login )

        always = DummyPlugin()
        directlyProvides( always, ( IAuthenticationPlugin, ) )
        always.authenticateCredentials = lambda creds: ('baz', None)

        zcuf._setObject( 'always', always )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IExtractionPlugin, 'login' )
        plugins.activatePlugin( IAuthenticationPlugin, 'always' )
        plugins.activatePlugin( IAuthenticationPlugin, 'login' )

        request = FauxRequest( form={ 'login' : 'foo', 'password' : 'bar' } )

        user_ids = zcuf._extractUserIds( request=request
                                       , plugins=zcuf.plugins
                                       )

        self.assertEqual( len( user_ids ), 2 )
        self.assertEqual( user_ids[ 0 ][0], 'always__baz' )
        self.assertEqual( user_ids[ 1 ][0], 'login__foo' )

    def test__extractUserIds_two_extractors_two_authenticators( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin, IAuthenticationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        login = DummyPlugin()
        directlyProvides( login, ( IExtractionPlugin, IAuthenticationPlugin ) )
        login.extractCredentials = _extractLogin
        login.authenticateCredentials = _authLogin

        zcuf._setObject( 'login', login )

        extra = DummyPlugin()
        directlyProvides( extra, ( IExtractionPlugin, IAuthenticationPlugin ) )
        extra.extractCredentials = _extractExtra
        extra.authenticateCredentials = _authExtra

        zcuf._setObject( 'extra', extra )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IExtractionPlugin, 'extra' )
        plugins.activatePlugin( IExtractionPlugin, 'login' )
        plugins.activatePlugin( IAuthenticationPlugin, 'extra' )
        plugins.activatePlugin( IAuthenticationPlugin, 'login' )

        request = FauxRequest( form={ 'login' : 'foo', 'password' : 'bar' } )

        user_ids = zcuf._extractUserIds( request=request
                                       , plugins=zcuf.plugins
                                       )

        self.assertEqual( len( user_ids ), 1 )
        self.assertEqual( user_ids[ 0 ][0], 'login__foo' )

        request[ 'extra' ] = 'qux'

        user_ids = zcuf._extractUserIds( request=request
                                       , plugins=zcuf.plugins
                                       )

        self.assertEqual( len( user_ids ), 2, user_ids )
        self.assertEqual( user_ids[ 0 ][0], 'extra__qux' )
        self.assertEqual( user_ids[ 1 ][0], 'login__foo' )

    def test__extractUserIds_broken_extractor( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin, IAuthenticationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        login = DummyPlugin()
        directlyProvides( login, ( IExtractionPlugin, IAuthenticationPlugin ) )
        login.extractCredentials = _extractLogin
        login.authenticateCredentials = _authLogin

        zcuf._setObject( 'login', login )

        borked = DummyPlugin()
        directlyProvides( borked, ( IExtractionPlugin, ) )
        borked.extractCredentials = lambda req: 'abc'

        zcuf._setObject( 'borked', borked )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IExtractionPlugin, 'borked' )
        plugins.activatePlugin( IExtractionPlugin, 'login' )
        plugins.activatePlugin( IAuthenticationPlugin, 'login' )

        request = FauxRequest( form={ 'login' : 'foo', 'password' : 'bar' } )

        user_ids = zcuf._extractUserIds( request=request
                                       , plugins=zcuf.plugins
                                       )

        self.assertEqual( len( user_ids ), 1 )
        self.assertEqual( user_ids[ 0 ][0], 'login__foo' )

    def test_authenticate_emergency_user_with_broken_extractor( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin, IAuthenticationPlugin

        from AccessControl.User import UnrestrictedUser

        from Products.PluggableAuthService import PluggableAuthService

        old_eu = PluggableAuthService.emergency_user

        eu = UnrestrictedUser( 'foo', 'bar', ( 'manage', ), () )

        PluggableAuthService.emergency_user = eu

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        borked = DummyPlugin()
        directlyProvides( borked, ( IExtractionPlugin, ) )
        borked.extractCredentials = lambda req: 'abc'

        zcuf._setObject( 'borked', borked )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IExtractionPlugin, 'borked' )

        request = FauxRequest( form={ 'login' : eu.getUserName()
                                    , 'password' : eu._getPassword() } )

        user_ids = zcuf._extractUserIds( request=request
                                       , plugins=zcuf.plugins
                                       )

        self.assertEqual( len( user_ids ), 1 )
        self.assertEqual( user_ids[ 0 ][0], 'foo' )

        PluggableAuthService.emergency_user = old_eu

    def test__extractUserIds_broken_authenticator( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin, IAuthenticationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        login = DummyPlugin()
        directlyProvides( login, ( IExtractionPlugin, IAuthenticationPlugin ) )
        login.extractCredentials = _extractLogin
        login.authenticateCredentials = _authLogin

        zcuf._setObject( 'login', login )

        borked = DummyPlugin()
        directlyProvides( borked, ( IAuthenticationPlugin, ) )
        borked.authenticateCredentials = lambda creds: creds['nonesuch']

        zcuf._setObject( 'borked', borked )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IExtractionPlugin, 'login' )
        plugins.activatePlugin( IAuthenticationPlugin, 'borked' )
        plugins.activatePlugin( IAuthenticationPlugin, 'login' )

        request = FauxRequest( form={ 'login' : 'foo', 'password' : 'bar' } )

        user_ids = zcuf._extractUserIds( request=request
                                       , plugins=zcuf.plugins
                                       )

        self.assertEqual( len( user_ids ), 1 )
        self.assertEqual( user_ids[ 0 ][0], 'login__foo' )

    def test__getObjectContext_no_steps( self ):

        zcuf = self._makeOne()
        request = FauxRequest( (), RESPONSE=FauxResponse() )

        self.assertRaises( FauxNotFoundError
                         , zcuf._getObjectContext, zcuf, request )

    def test__getObjectContext_simple( self ):

        zcuf = self._makeOne()

        rc, root, folder, object = self._makeTree()

        local_index = FauxObject( 'index_html' ).__of__( object )

        request = FauxRequest( ( 'folder', 'object', 'index_html' )
                             , RESPONSE=FauxResponse()
                             , PARENTS=[ object, folder, root ]
                             )

        published = local_index

        a, c, n, v = zcuf._getObjectContext( published, request )

        self.assertEqual( a, object )
        self.assertEqual( c, object )
        self.assertEqual( n, 'index_html' )
        self.assertEqual( v, published )

    def test__getObjectContext_acquired_from_folder( self ):

        zcuf = self._makeOne()

        rc, root, folder, object = self._makeTree()

        acquired_index = FauxObject( 'index_html' ).__of__( folder )

        request = FauxRequest( ( 'folder', 'object', 'index_html' )
                             , RESPONSE=FauxResponse()
                             , PARENTS=[ object, folder, root ]
                             )

        published = acquired_index.__of__( object )

        a, c, n, v = zcuf._getObjectContext( published, request )

        self.assertEqual( a, object )
        self.assertEqual( c, folder )
        self.assertEqual( n, 'index_html' )
        self.assertEqual( v, published )

    def test__getObjectContext_acquired_from_root( self ):

        zcuf = self._makeOne()

        rc, root, folder, object = self._makeTree()

        acquired_index = FauxObject( 'index_html' ).__of__( root )

        request = FauxRequest( ( 'folder', 'object', 'index_html' )
                             , RESPONSE=FauxResponse()
                             , PARENTS=[ object, folder, root ]
                             )

        published = acquired_index.__of__( object )

        a, c, n, v = zcuf._getObjectContext( published, request )

        self.assertEqual( a, object )
        self.assertEqual( c, root )
        self.assertEqual( n, 'index_html' )
        self.assertEqual( v, published )


    def test__getObjectContext_acquired_from_rc( self ):

        zcuf = self._makeOne()

        rc, root, folder, object = self._makeTree()

        acquired_index = FauxObject( 'index_html' ).__of__( rc )

        request = FauxRequest( ( 'folder', 'object', 'index_html' )
                             , RESPONSE=FauxResponse()
                             , PARENTS=[ object, folder, root ]
                             )

        published = acquired_index.__of__( object )

        a, c, n, v = zcuf._getObjectContext( published, request )

        self.assertEqual( a, object )
        self.assertEqual( c, root )
        self.assertEqual( n, 'index_html' )
        self.assertEqual( v, published )


    def test__verifyUser_no_plugins( self ):

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        self.failIf( zcuf._verifyUser( zcuf.plugins, user_id='zope' ) )

    def test__verifyUser_one_plugin( self ):

        from Products.PluggableAuthService.interfaces.plugins \
             import IUserEnumerationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        foo = self._makeUserEnumerator( 'foo' )
        zcuf._setObject( 'foo', foo )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IUserEnumerationPlugin, 'foo' )

        self.failIf(      zcuf._verifyUser( zcuf.plugins, user_id='zope' ) )
        self.failUnless(  zcuf._verifyUser( zcuf.plugins, user_id='foo' ) )

    def test__verifyUser_more_plugins( self ):

        from Products.PluggableAuthService.interfaces.plugins \
             import IUserEnumerationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        foo = self._makeUserEnumerator( 'foo' )
        zcuf._setObject( 'foo', foo )

        bar = self._makeUserEnumerator( 'bar' )
        zcuf._setObject( 'bar', bar )

        qux = self._makeUserEnumerator( 'qux' )
        zcuf._setObject( 'qux', qux )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IUserEnumerationPlugin, 'foo' )
        plugins.activatePlugin( IUserEnumerationPlugin, 'bar' )
        plugins.activatePlugin( IUserEnumerationPlugin, 'qux' )

        self.failIf(      zcuf._verifyUser( zcuf.plugins, user_id='zope' ) )
        self.failUnless(  zcuf._verifyUser( zcuf.plugins, user_id='foo' ) )
        self.failUnless(  zcuf._verifyUser( zcuf.plugins, user_id='bar' ) )
        self.failIf(      zcuf._verifyUser( zcuf.plugins, user_id='baz' ) )
        self.failUnless(  zcuf._verifyUser( zcuf.plugins, user_id='qux' ) )

    def test__verifyUser_login( self ):

        from Products.PluggableAuthService.interfaces.plugins \
             import IUserEnumerationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        foo = self._makeUserEnumerator( 'foo' )
        zcuf._setObject( 'foo', foo )

        bar = self._makeUserEnumerator( 'bar', 'bar@example.com' )
        zcuf._setObject( 'bar', bar )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IUserEnumerationPlugin, 'foo' )
        plugins.activatePlugin( IUserEnumerationPlugin, 'bar' )

        self.failIf(      zcuf._verifyUser( zcuf.plugins, login='zope' ) )
        self.failUnless(  zcuf._verifyUser( zcuf.plugins, login='foo' ) )
        self.failIf(      zcuf._verifyUser( zcuf.plugins, login='bar' ) )
        self.failUnless(  zcuf._verifyUser( zcuf.plugins
                                          , login='bar@example.com' ) )

    def test__findUser_no_plugins( self ):

        plugins = self._makePlugins()

        zcuf = self._makeOne()
        user = zcuf._findUser( plugins, 'someone' )

        self.assertEqual( len( user.listPropertysheets() ), 0 )

    def test__findEmergencyUser_no_plugins( self ):

        from AccessControl.User import UnrestrictedUser

        from Products.PluggableAuthService import PluggableAuthService

        old_eu = PluggableAuthService.emergency_user

        eu = UnrestrictedUser( 'foo', 'bar', ( 'manage', ), () )

        PluggableAuthService.emergency_user = eu

        plugins = self._makePlugins()
        zcuf = self._makeOne()
        zcuf._emergency_user = eu
        user = zcuf._findUser( plugins, 'foo' )

        self.assertEqual( aq_base(zcuf._getEmergencyUser()), aq_base(user) )

        PluggableAuthService.emergency_user = old_eu

    def test__findUser_with_userfactory_plugin( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IUserFactoryPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        bar = DummyPlugin()
        directlyProvides( bar, ( IUserFactoryPlugin, ) )

        def _makeUser( user_id, name ):
            user = FauxUser( user_id )
            user._name = name
            return user

        bar.createUser = _makeUser

        zcuf._setObject( 'bar', bar )

        plugins = zcuf._getOb( 'plugins' )

        real_user = zcuf._findUser( plugins, 'someone', 'to watch over me' )
        self.failIf( real_user.__class__ is FauxUser )

        plugins.activatePlugin( IUserFactoryPlugin , 'bar' )

        faux_user = zcuf._findUser( plugins, 'someone', 'to watch over me' )

        self.assertEqual( faux_user.getId(), 'someone' )
        self.assertEqual( faux_user.getUserName(), 'to watch over me' )

        self.failUnless( faux_user.__class__ is FauxUser )

    def test__findUser_with_plugins( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IPropertiesPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        foo = DummyPlugin()
        directlyProvides( foo, ( IPropertiesPlugin, ) )
        foo.getPropertiesForUser = lambda user, req: { 'login': user.getId() }

        zcuf._setObject( 'foo', foo )

        bar = DummyPlugin()
        directlyProvides( bar, ( IPropertiesPlugin, ) )
        bar.getPropertiesForUser = lambda user, req: { 'a': 0, 'b': 'bar' }

        zcuf._setObject( 'bar', bar )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IPropertiesPlugin , 'foo' )
        plugins.activatePlugin( IPropertiesPlugin , 'bar' )

        user = zcuf._findUser( plugins, 'someone' )

        sheet_ids = user.listPropertysheets()
        self.assertEqual( len( sheet_ids ), 2 )
        self.failUnless( 'foo' in sheet_ids )
        self.failUnless( 'bar' in sheet_ids )

        foosheet = user[ 'foo' ]
        self.assertEqual( len( foosheet.propertyMap() ), 1 )

    def test__findUser_with_groups( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IGroupsPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        foo = DummyPlugin()
        directlyProvides( foo, ( IGroupsPlugin, ) )
        foo.getGroupsForPrincipal = lambda user, req: ( 'group1', 'group2' )

        zcuf._setObject( 'foo', foo )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IGroupsPlugin , 'foo' )

        user = zcuf._findUser( plugins, 'someone' )

        groups = user.getGroups()
        self.assertEqual( len( groups ), 2 )
        self.failUnless( 'foo__group1' in groups )
        self.failUnless( 'foo__group2' in groups )

    def test__findUser_with_groups_ignoring_one( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IGroupsPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        foo = DummyPlugin()
        directlyProvides( foo, ( IGroupsPlugin, ) )
        foo.getGroupsForPrincipal = lambda user, req: ( 'group1', 'group2' )

        bar = DummyPlugin()
        directlyProvides( bar, ( IGroupsPlugin, ) )
        bar.getGroupsForPrincipal = lambda user, req: ( 'group3', 'group4' )

        zcuf._setObject( 'foo', foo )
        zcuf._setObject( 'bar', bar )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IGroupsPlugin , 'foo' )
        plugins.activatePlugin( IGroupsPlugin , 'bar' )

        user = zcuf._findUser( plugins, 'someone' )

        groups = zcuf._getGroupsForPrincipal( user, plugins=plugins
                                            , ignore_plugins=( 'bar', ) )
        self.assertEqual( len( groups ), 2 )
        self.failIf( 'bar:group3' in groups )
        self.failIf( 'bar:group4' in groups )

    def test__authorizeUser_force_ok( self ):

        zcuf = self._makeOne()
        faux = FauxUser( 'faux' )

        class PermissiveSP:

            def validate( self
                        , user
                        , accessed
                        , container
                        , name
                        , value
                        , roles=None
                        ):
                return 1

        self._oldSecurityPolicy = setSecurityPolicy( PermissiveSP() )

        self.failUnless( zcuf._authorizeUser( faux
                                            , accessed=FauxObject('a')
                                            , container=FauxObject('c')
                                            , name='name'
                                            , value=FauxObject('v')
                                            , roles=()
                                            ) )

    def test__authorizeUser_force_no_way( self ):

        zcuf = self._makeOne()
        faux = FauxUser( 'faux' )

        class ParanoidSP:

            def validate( self
                        , user
                        , accessed
                        , container
                        , name
                        , value
                        , roles=None
                        ):
                return 0

        self._oldSecurityPolicy = setSecurityPolicy( ParanoidSP() )

        self.failIf( zcuf._authorizeUser( faux
                                        , accessed=FauxObject('a')
                                        , container=FauxObject('c')
                                        , name='name'
                                        , value=FauxObject('v')
                                        , roles=()
                                        ) )

    def test__authorizeUser_use_ZSP_implied_roles_OK( self ):

        zcuf = self._makeOne()
        faux = FauxUser( 'faux' )
        object = FauxObject( 'object' )
        object.__roles__ = ( 'Anonymous', )

        self.failUnless( zcuf._authorizeUser( faux
                                            , accessed=FauxObject('a')
                                            , container=FauxObject('c')
                                            , name='name'
                                            , value=object
                                            ) )

    def test__authorizeUser_use_ZSP_implied_roles_fail( self ):

        zcuf = self._makeOne()
        faux = FauxUser( 'faux' )
        object = FauxObject( 'object' )
        object.__roles__ = ( 'Manager', )

        self.failIf( zcuf._authorizeUser( faux
                                        , accessed=FauxObject('a')
                                        , container=FauxObject('c')
                                        , name='name'
                                        , value=object
                                        ) )

    def test__authorizeUser_use_ZSP_implied_roles_mgr( self ):

        zcuf = self._makeOne()
        mgr = FauxUser( 'mgr', roles=( 'Manager', ) )
        object = FauxObject( 'object' )
        object.__roles__ = ( 'Manager', )

        self.failUnless( zcuf._authorizeUser( mgr
                                            , accessed=FauxObject('a')
                                            , container=FauxObject('c')
                                            , name='name'
                                            , value=object
                                            ) )

    def test__authorizeUser_use_ZSP_explicit_roles_OK( self ):

        zcuf = self._makeOne()
        faux = FauxUser( 'faux' )
        object = FauxObject( 'object' )

        self.failUnless( zcuf._authorizeUser( faux
                                            , accessed=FauxObject('a')
                                            , container=FauxObject('c')
                                            , name='name'
                                            , value=object
                                            , roles=('Anonymous',)
                                            ) )

    def test__authorizeUser_use_ZSP_explicit_roles_fail( self ):

        zcuf = self._makeOne()
        faux = FauxUser( 'faux' )
        object = FauxObject( 'object' )

        self.failIf( zcuf._authorizeUser( faux
                                        , accessed=FauxObject('a')
                                        , container=FauxObject('c')
                                        , name='name'
                                        , value=object
                                        , roles=('Manager',)
                                        ) )

    def test__authorizeUser_use_ZSP_explicit_roles_mgr( self ):

        zcuf = self._makeOne()
        mgr = FauxUser( 'mgr', roles=( 'Manager', ) )
        object = FauxObject( 'object' )

        self.failUnless( zcuf._authorizeUser( mgr
                                            , accessed=FauxObject('a')
                                            , container=FauxObject('c')
                                            , name='name'
                                            , value=object
                                            , roles=('Manager',)
                                            ) )

    def test_getUser_no_plugins( self ):

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        self.assertEqual(  zcuf.getUser( 'zope' ), None )

    def test_getUser_with_plugins( self ):

        from Products.PluggableAuthService.interfaces.plugins \
             import IUserEnumerationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        foo = self._makeUserEnumerator( 'foo' )
        zcuf._setObject( 'foo', foo )

        bar = self._makeUserEnumerator( 'bar', 'bar@example.com' )
        zcuf._setObject( 'bar', bar )

        plugins = zcuf._getOb( 'plugins' )

        plugins.activatePlugin( IUserEnumerationPlugin, 'foo' )
        plugins.activatePlugin( IUserEnumerationPlugin, 'bar' )

        self.assertEqual( zcuf.getUser( 'zope' ), None )

        user = zcuf.getUser( 'foo' )
        self.assertEqual( user.getId(), 'foo__foo' )

        self.assertEqual( zcuf.getUser( 'foo__bar' ), None )

        user = zcuf.getUser( 'bar@example.com' )
        self.assertEqual( user.getId(), 'bar__bar' )

    def test_simple_getUserGroups_with_Groupplugin(self):

        from Products.PluggableAuthService.interfaces.plugins \
             import IGroupsPlugin

        default_groups = ('Group A', 'Group B')
        plugins = self._makePlugins()
        zcuf = self._makeOne(plugins)
        faux = FauxUser('faux')

        foo = self._makeGroupPlugin('foo', groups=default_groups)
        zcuf._setObject('foo', foo)

        plugins = zcuf._getOb('plugins')

        plugins.activatePlugin(IGroupsPlugin, 'foo')

        groups = foo.getGroupsForPrincipal(faux)
        for g in groups:
            self.assert_(g in default_groups)

        faux._addGroups(groups)

        self.assert_('Group A' in faux.getGroups())
        self.assert_('Group B' in faux.getGroups())

    def test_validate_simple_unauth( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin, \
                   IAuthenticationPlugin, \
                   IUserEnumerationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        login = DummyPlugin()
        directlyProvides( login, ( IExtractionPlugin, IAuthenticationPlugin ) )
        login.extractCredentials = _extractLogin
        login.authenticateCredentials = _authLogin
        zcuf._setObject( 'login', login )

        foo = DummyPlugin()
        directlyProvides( foo, ( IUserEnumerationPlugin, ) )
        foo.enumerateUsers = lambda id: id == 'foo' or None

        zcuf._setObject( 'foo', foo )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IExtractionPlugin, 'login' )
        plugins.activatePlugin( IAuthenticationPlugin, 'login' )
        plugins.activatePlugin( IUserEnumerationPlugin, 'foo' )

        rc, root, folder, object = self._makeTree()

        index = FauxObject( 'index_html' )
        index.__roles__ = ( 'Hamlet', )
        acquired_index = index.__of__( root ).__of__( object )

        request = FauxRequest( ( 'folder', 'object', 'index_html' )
                             , RESPONSE=FauxResponse()
                             , PARENTS=[ object, folder, root ]
                             , PUBLISHED=acquired_index
                             , form={ 'login' : 'foo', 'password' : 'bar' }
                             )


        wrapped = zcuf.__of__( root )
        validated = wrapped.validate( request )
        self.assertEqual( validated, None )

    def test_validate_simple_anonymous( self ):

        from AccessControl.SpecialUsers import nobody

        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin, \
                   IAuthenticationPlugin, \
                   IUserEnumerationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        login = DummyPlugin()
        directlyProvides( login, ( IExtractionPlugin, IAuthenticationPlugin ) )
        login.extractCredentials = _extractLogin
        login.authenticateCredentials = _authLogin
        zcuf._setObject( 'login', login )

        foo = DummyPlugin()
        directlyProvides( foo, ( IUserEnumerationPlugin, ) )
        foo.enumerateUsers = lambda id: id == 'foo' or None

        zcuf._setObject( 'foo', foo )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IExtractionPlugin, 'login' )
        plugins.activatePlugin( IAuthenticationPlugin, 'login' )
        plugins.activatePlugin( IUserEnumerationPlugin, 'foo' )

        rc, root, folder, object = self._makeTree()

        index = FauxObject( 'index_html' )
        index.__roles__ = ( 'Anonymous', )
        acquired_index = index.__of__( root ).__of__( object )

        request = FauxRequest( ( 'folder', 'object', 'index_html' )
                             , RESPONSE=FauxResponse()
                             , PARENTS=[ object, folder, root ]
                             , PUBLISHED=acquired_index
                             , form={}
                             )


        wrapped = zcuf.__of__( root )
        validated = wrapped.validate( request )
        self.assertEqual( validated.getUserName(), nobody.getUserName() )

    def test_validate_simple_authenticated( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin, \
                   IAuthenticationPlugin, \
                   IUserEnumerationPlugin, \
                   IRolesPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        login = DummyPlugin()
        directlyProvides( login, ( IExtractionPlugin, IAuthenticationPlugin ) )
        login.extractCredentials = _extractLogin
        login.authenticateCredentials = _authLogin
        zcuf._setObject( 'login', login )

        olivier = DummyPlugin()
        directlyProvides( olivier, ( IUserEnumerationPlugin, IRolesPlugin ) )
        olivier.enumerateUsers = lambda id: id == 'foo' or None
        olivier.getRolesForPrincipal = lambda user, req: (
                     user.getId() == 'login__olivier' and ( 'Hamlet', ) or () )

        zcuf._setObject( 'olivier', olivier )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IExtractionPlugin, 'login' )
        plugins.activatePlugin( IAuthenticationPlugin, 'login' )
        plugins.activatePlugin( IUserEnumerationPlugin, 'olivier' )
        plugins.activatePlugin( IRolesPlugin, 'olivier' )

        rc, root, folder, object = self._makeTree()

        index = FauxObject( 'index_html' )
        index.__roles__ = ( 'Hamlet', )
        acquired_index = index.__of__( root ).__of__( object )

        request = FauxRequest( ( 'folder', 'object', 'index_html' )
                             , RESPONSE=FauxResponse()
                             , PARENTS=[ object, folder, root ]
                             , PUBLISHED=acquired_index.__of__( object )
                             , form={ 'login' : 'olivier'
                                    , 'password' : 'arras'
                                    }
                             )


        wrapped = zcuf.__of__( root )

        validated = wrapped.validate( request )
        self.assertEqual( validated.getUserName(), 'olivier' )

    def test_validate_with_anonymous_factory( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IAnonymousUserFactoryPlugin

        def _makeAnon():
            user = FauxUser( None
                           , name='New Anonymous User'
                           , roles=()
                           , groups={ 'All People Everywhere Ever' : 1 } )
            return user

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )
        nested = self._makeOne( plugins )

        anon = DummyPlugin()
        directlyProvides( anon, ( IAnonymousUserFactoryPlugin, ) )
        anon.createAnonymousUser = _makeAnon
        zcuf._setObject( 'anon', anon )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IAnonymousUserFactoryPlugin, 'anon' )

        rc, root, folder, object = self._makeTree()

        index = FauxObject( 'index_html' )
        index.__roles__ = ( 'Anonymous', )
        acquired_index = index.__of__( root ).__of__( object )

        request = FauxRequest( ( 'folder', 'object', 'index_html' )
                             , RESPONSE=FauxResponse()
                             , PARENTS=[ object, folder, root ]
                             , PUBLISHED=acquired_index
                             , form={}
                             )

        root._setObject( 'acl_users', zcuf )
        root_users = root.acl_users

        root_validated = root_users.validate( request )
        self.assertEqual( root_validated.getUserName(), 'New Anonymous User' )
        self.assertEqual( root_validated.getGroups()
                        , [ 'All People Everywhere Ever' ] )

    def testAllowGroupsAttribute(self):
        # Verify that __allow_groups__ gets set and removed
        from OFS.Folder import Folder
        f = Folder()
        zcuf = self._makeOne()
        f._setObject(zcuf.getId(), zcuf)
        self.assert_(zcuf.getId() in f.objectIds())
        self.assert_(aq_base(f.__allow_groups__) is aq_base(f.acl_users))
        f._delObject(zcuf.getId())
        self.assert_(not zcuf.getId() in f.objectIds())

    def test__setObject_no_ownership_fixup( self ):

        from AccessControl.SpecialUsers import emergency_user
        from OFS.Folder import Folder

        newSecurityManager( None, emergency_user )

        rc, root, folder, object = self._makeTree()
        zcuf = self._makeOne()
        folder._setObject( 'acl_users', zcuf )
        zcuf = folder._getOb( 'acl_users' )

        sub = Folder()
        sub._setId( 'sub' )

        zcuf._setObject( 'sub', sub )

    def test__delOb_unregisters_plugin( self ):

        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin, \
                   IAuthenticationPlugin, \
                   IUserEnumerationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        login = DummyPlugin()
        directlyProvides( login, ( IExtractionPlugin, IAuthenticationPlugin ) )
        login.extractCredentials = _extractLogin
        login.authenticateCredentials = _authLogin
        zcuf._setObject( 'login', login )

        foo = DummyPlugin()
        directlyProvides( foo, ( IUserEnumerationPlugin, ) )
        foo.enumerateUsers = lambda id: id == 'foo' or None

        zcuf._setObject( 'foo', foo )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IExtractionPlugin, 'login' )
        plugins.activatePlugin( IAuthenticationPlugin, 'login' )
        plugins.activatePlugin( IUserEnumerationPlugin, 'foo' )

        self.failUnless( plugins.listPlugins( IExtractionPlugin ) )
        self.failUnless( plugins.listPlugins( IAuthenticationPlugin ) )
        self.failUnless( plugins.listPlugins( IUserEnumerationPlugin ) )

        zcuf._delOb( 'foo' )

        self.failUnless( plugins.listPlugins( IExtractionPlugin ) )
        self.failUnless( plugins.listPlugins( IAuthenticationPlugin ) )
        self.failIf( plugins.listPlugins( IUserEnumerationPlugin ) )

        zcuf._delOb( 'login' )

        self.failIf( plugins.listPlugins( IExtractionPlugin ) )
        self.failIf( plugins.listPlugins( IAuthenticationPlugin ) )
        self.failIf( plugins.listPlugins( IUserEnumerationPlugin ) )

    def test_searchGroups( self ):

        from Products.PluggableAuthService.interfaces.plugins \
             import IGroupEnumerationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        foo = self._makeGroupEnumerator( 'foo' )
        zcuf._setObject( 'foo', foo )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IGroupEnumerationPlugin, 'foo' )

        self.failIf(      zcuf.searchGroups( id='bar' ) )
        self.failUnless(  zcuf.searchGroups( id='foo' ) )
        self.assertEqual( len(zcuf.searchGroups( id='foo' )), 1 )

    def test_searchPrincipals( self ):

        from Products.PluggableAuthService.interfaces.plugins \
             import IUserEnumerationPlugin
        from Products.PluggableAuthService.interfaces.plugins \
             import IGroupEnumerationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        foo = self._makeUserEnumerator( 'foo' )
        zcuf._setObject( 'foo', foo )
        foobar = self._makeGroupEnumerator( 'foobar' )
        zcuf._setObject( 'foobar', foobar )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IUserEnumerationPlugin, 'foo' )
        plugins.activatePlugin( IGroupEnumerationPlugin, 'foobar' )

        self.failIf(      zcuf.searchPrincipals( id='zope' ) )
        self.failUnless(  len( zcuf.searchPrincipals( id='foo__foo'
                                                    , exact_match=True )
                               ) == 1 )
        self.failUnless(  len( zcuf.searchPrincipals( id='foo'
                                                    , exact_match=False )
                               ) == 2 )

    def test_searchPrincipalsWithSuperEnumerator( self ):

        from Products.PluggableAuthService.interfaces.plugins \
             import IUserEnumerationPlugin
        from Products.PluggableAuthService.interfaces.plugins \
             import IGroupEnumerationPlugin

        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        s00per = self._makeSuperEnumerator( 'user', 'login', 'group' )
        zcuf._setObject( 's00per', s00per )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IUserEnumerationPlugin, 's00per' )
        plugins.activatePlugin( IGroupEnumerationPlugin, 's00per' )

        self.failIf(      zcuf.searchPrincipals( id='zope' ) )
        self.failUnless(
            len( zcuf.searchPrincipals( id='s00per__user'
                                      , exact_match=True ) ) == 1 )
        self.failUnless(
            len( zcuf.searchPrincipals( id='s00per__group'
                                      , exact_match=True ) ) == 1 )


    def test_no_challenger(self):
        # make sure that the response's _unauthorized gets propogated
        # if no challengers exist (or have fired)
        plugins = self._makePlugins()
        zcuf = self._makeOne(plugins)
        response = FauxResponse()
        request = FauxRequest(RESPONSE=response)
        zcuf.REQUEST = request

        # First call the userfolders before_traverse hook, to set things up:
        zcuf(self, request)
        # Call unauthorized to make sure Unauthorized is raised.
        self.failUnlessRaises( Unauthorized, response.unauthorized)
        # Since no challengers are in play, we end up calling
        # response._unauthorized(), which sets '.challenger' on
        # response
        self.failUnless(isinstance(response.challenger, FauxResponse))

    def test_challenge( self ):
        from Products.PluggableAuthService.interfaces.plugins \
             import IChallengePlugin
        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )
        challenger = self._makeChallengePlugin('challenger', DummyChallenger)
        zcuf._setObject( 'challenger', challenger )
        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IChallengePlugin, 'challenger' )

        response = FauxResponse()
        request = FauxRequest(RESPONSE=response)
        zcuf.REQUEST = request

        # First call the userfolders before_traverse hook, to set things up:
        zcuf(self, request)
        # Call unauthorized to make sure Unauthorized is raised.
        self.failUnlessRaises( Unauthorized, response.unauthorized)
        # Since we have one challenger in play, we end up calling
        # PluggableAuthService._unauthorized(), which allows the
        # challengers to play. DummyChallenger sets '.challenger' on
        # response
        self.failUnless(isinstance(response.challenger, DummyChallenger))

    def test_daisy_chain_challenge(self):
        # make sure that nested PASes each get a chance to challenge a
        # given response
        from Products.PluggableAuthService.interfaces.plugins \
             import IChallengePlugin
        rc, root, folder, object = self._makeTree()
        response = FauxResponse()
        request = FauxRequest(RESPONSE=response)
        root.REQUEST =  request

        plugins = self._makePlugins()
        zcuf = self._makeOne(plugins)
        root._setObject( 'acl_users', zcuf )
        zcuf = root._getOb('acl_users')

        challenger = self._makeChallengePlugin('challenger', DummyChallenger)
        zcuf._setObject( 'challenger', challenger )
        zcuf.plugins.activatePlugin( IChallengePlugin, 'challenger' )

        # Emulate publishing traverse through the root
        zcuf(root, request)

        inner_plugins = self._makePlugins()
        inner_zcuf = self._makeOne(inner_plugins)
        folder._setObject('acl_users', inner_zcuf)
        inner_zcuf = folder._getOb('acl_users')

        bad_challenger = self._makeChallengePlugin('bad_challenger',
                                                   DummyBadChallenger)
        inner_zcuf._setObject( 'bad_challenger', bad_challenger )
        inner_zcuf.plugins.activatePlugin( IChallengePlugin, 'bad_challenger' )

        # Emulate publishing traverse through the subfolder
        inner_zcuf(folder, request)

        # Call unauthorized to make sure Unauthorized is raised.
        self.failUnlessRaises(Unauthorized, response.unauthorized)

        # Since we have two challengers in play, we end up calling
        # PluggableAuthService._unauthorized(), which allows the
        # challengers to play. DummyChallenger sets '.challenger' on
        # response
        self.failUnless(isinstance(response.challenger, DummyChallenger))

    def test_challenge_multi_protocols( self ):
        from Products.PluggableAuthService.interfaces.plugins \
             import IChallengePlugin
        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        dasher = self._makeChallengePlugin('dasher', DummyReindeerChallenger)
        dasher.protocol = "Reindeer Games Participant"
        zcuf._setObject( 'dasher', dasher )

        dancer = self._makeChallengePlugin('dancer', DummyReindeerChallenger)
        dancer.protocol = "Reindeer Games Participant"
        zcuf._setObject( 'dancer', dancer )

        rudolph = self._makeChallengePlugin('rudolph', DummyReindeerChallenger)
        rudolph.protocol = ("They never let poor Rudolph..."
                            " join in any Reindeer Games")
        zcuf._setObject( 'rudolph', rudolph )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IChallengePlugin, 'dasher' )
        plugins.activatePlugin( IChallengePlugin, 'dancer' )
        plugins.activatePlugin( IChallengePlugin, 'rudolph' )

        response = FauxResponse()
        request = FauxRequest(RESPONSE=response)
        zcuf.REQUEST = request

        # First call the userfolders before_traverse hook, to set things up:
        zcuf(self, request)

        # Call unauthorized to make sure Unauthorized is raised.
        self.failUnlessRaises( Unauthorized, response.unauthorized)

        # Since we have multiple challengers in play, we end up
        # calling PluggableAuthService._unauthorized(), which allows
        # the challengers to play. However, because of the ordering of
        # the plugins, only "Reindeer Games Participant" challengers
        # will play
        self.assertEqual(response.reindeer_games, ['dasher', 'dancer'])

    def test_dont_call_challenge_twice(self):
        from Products.PluggableAuthService.interfaces.plugins \
             import IChallengePlugin
        plugins = self._makePlugins()
        zcuf = self._makeOne( plugins )

        counter = self._makeChallengePlugin('counter', DummyCounterChallenger)
        zcuf._setObject( 'counter', counter )

        plugins = zcuf._getOb( 'plugins' )
        plugins.activatePlugin( IChallengePlugin, 'counter' )

        response = FauxResponse()
        request = FauxRequest(RESPONSE=response)
        zcuf.REQUEST = request

        zcuf(self, request)

        self.failUnlessRaises( Unauthorized, response.unauthorized)

        self.assertEqual(counter.count, 1)

if __name__ == "__main__":
    unittest.main()

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( PluggableAuthServiceTests ),
        ))

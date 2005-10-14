import unittest

from Products.PluggableAuthService.tests.conformance \
    import IGroupEnumerationPlugin_conformance
from Products.PluggableAuthService.tests.conformance \
    import IGroupsPlugin_conformance

from Products.PluggableAuthService.tests.test_PluggableAuthService \
    import FauxContainer

class FauxPAS( FauxContainer ):

    def __init__( self ):
        self._id = 'acl_users'
        
    def searchPrincipals( self, **kw ):
        id = kw.get( 'id' )
        return [ { 'id': id } ]

class DummyGroup:

    def __init__( self, id ):
        self._id = id

    def getId( self ):
        return self._id

class DummyUser:

    def __init__( self, id ):
        self._id = id

    def getId( self ):
        return self._id

class ZODBGroupManagerTests( unittest.TestCase
                           , IGroupEnumerationPlugin_conformance
                           , IGroupsPlugin_conformance
                           ):

    def _getTargetClass( self ):

        from Products.PluggableAuthService.plugins.ZODBGroupManager \
            import ZODBGroupManager

        return ZODBGroupManager

    def _makeOne( self, id='test', *args, **kw ):

        return self._getTargetClass()( id=id, *args, **kw )

    def test_empty( self ):

        zgm = self._makeOne()

        self.assertEqual( len( zgm.listGroupIds() ), 0 )
        self.assertEqual( len( zgm.enumerateGroups() ), 0 )

        user = DummyUser( 'userid' )
        groups = zgm.getGroupsForPrincipal( user )
        self.assertEqual( len( groups ), 0 )

    def test_addGroup( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        zgm = self._makeOne().__of__( root )

        zgm.addGroup( 'group' )

        group_ids = zgm.listGroupIds()
        self.assertEqual( len( group_ids ), 1 )
        self.assertEqual( group_ids[0], 'group' )

        info_list = zgm.enumerateGroups()
        self.assertEqual( len( info_list ), 1 )
        info = info_list[ 0 ]
        self.assertEqual( info[ 'id' ], 'group' )

    def test_addGroup_exists( self ):

        zgm = self._makeOne()

        zgm.addGroup( 'group' )
        self.assertRaises( KeyError, zgm.addGroup, 'group' )

    def test_updateGroup_normal( self ):

        zgm = self._makeOne()

        zgm.addGroup( 'group', 'group_title', 'group_desc' )

        group_info = zgm.getGroupInfo( 'group' )
        self.assertEqual( group_info['title'], 'group_title' )
        zgm.updateGroup( 'group', 'group_title_changed', 'group_desc' )
        group_info = zgm.getGroupInfo( 'group' )
        self.assertEqual( group_info['title'], 'group_title_changed' )

    def test_addPrincipalToGroup( self ):

        zgm = self._makeOne()

        zgm.addGroup( 'group' )

        user = DummyUser( 'userid' )
        
        zgm.addPrincipalToGroup( user.getId(), 'group' )
        groups = zgm.getGroupsForPrincipal( user )
        self.assertEqual( groups, ( 'group', ) )

    def test_removePrincipalFromGroup( self ):

        zgm = self._makeOne()

        zgm.addGroup( 'group' )

        user = DummyUser( 'userid' )
        
        zgm.addPrincipalToGroup( user.getId(), 'group' )
        zgm.removePrincipalFromGroup( user.getId(), 'group' )
        groups = zgm.getGroupsForPrincipal( user )
        self.assertEqual( groups, () )

    def test_removeGroupOutFromUnderPrincipal( self ):

        zgm = self._makeOne()

        zgm.addGroup( 'group' )

        user = DummyUser( 'userid' )
        
        zgm.addPrincipalToGroup( user.getId(), 'group' )
        zgm.removeGroup( 'group' )
        group_ids = zgm.listGroupIds()
        self.assertEqual( len( group_ids ), 0 )
        groups = zgm.getGroupsForPrincipal( user )
        self.assertEqual( groups, () )

    def test_multiplePrincipalsPerGroup( self ):

        pas = FauxPAS()
        zgm = self._makeOne().__of__( pas )
        
        zgm.addGroup( 'group1' )
        zgm.addGroup( 'group2' )

        user1 = DummyUser( 'userid1' )
        user2 = DummyUser( 'userid2' )
        
        zgm.addPrincipalToGroup( user1.getId(), 'group1' )
        zgm.addPrincipalToGroup( user1.getId(), 'group2' )
        zgm.addPrincipalToGroup( user2.getId(), 'group2' )

        group_ids = zgm.listGroupIds()
        self.assertEqual( len( group_ids ), 2 )
        principals = zgm.listAssignedPrincipals( 'group2' )
        self.assertEqual( principals, [ ( 'userid1', 'userid1' ),
                                        ( 'userid2', 'userid2' ) ] )

    def test_enumerateGroups_exact_nonesuch( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        zgm = self._makeOne( id='exact_nonesuch' ).__of__( root )

        ID_LIST = ( 'foo', 'bar', 'baz', 'bam' )

        for id in ID_LIST:

            zgm.addGroup( id, 'Group %s' % id, 'This is group, %s' % id )

        self.assertEqual( zgm.enumerateGroups( id='qux', exact_match=True )
                        , () )

    def test_enumerateGroups_multiple( self ):

        from Products.PluggableAuthService.tests.test_PluggableAuthService \
            import FauxRoot

        root = FauxRoot()
        zrm = self._makeOne( id='partial' ).__of__( root )

        ID_LIST = ( 'foo', 'bar', 'baz', 'bam' )

        for id in ID_LIST:

            zrm.addGroup( id, 'Group %s' % id, 'This is group, %s' % id )

        info_list = zrm.enumerateGroups( id=ID_LIST, exact_match=False )

        self.assertEqual( len( info_list ), len( ID_LIST ) )

        for info in info_list:
            self.failUnless( info[ 'id' ] in ID_LIST )

        SUBSET = ID_LIST[:3]

        info_list = zrm.enumerateGroups( id=SUBSET, exact_match=False )

        self.assertEqual( len( info_list ), len( SUBSET ) )

        for info in info_list:
            self.failUnless( info[ 'id' ] in SUBSET )

if __name__ == "__main__":
    unittest.main()

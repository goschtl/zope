import unittest

class DefaultPredicateTests( unittest.TestCase ):

    def test_empty( self ):
        from Products.CMFCore.CachingTool import DefaultPredicate
        pred = DefaultPredicate( 'empty' )
        assert pred( None, 'any_name' )

class NameSuffixPredicateTests( unittest.TestCase ):

    def _makeOne( self, id ):
        from Products.CMFCore.CachingTool import NameSuffixPredicate
        return NameSuffixPredicate( id )

    def test_empty( self ):
        pred = self._makeOne( 'empty' )
        assert pred.getSkinNameSuffix() == ''
        assert not pred( None, 'any_name' )

    def test_simple( self ):
        pred = self._makeOne( 'views' )
        pred.edit( skin_name_suffix='_view' )
        assert pred.getSkinNameSuffix() == '_view'
        assert not pred( None, 'foo_bar' )
        assert pred( None, 'foo_view' )

class CachingToolRegistryTests( unittest.TestCase ):

    def _makeOne( self ):
        from Products.CMFCore.CachingTool import CachingTool
        return CachingTool()
        
    def test_empty( self ):
        reg = self._makeOne()
        assert reg.findCacheManagerID( None, 'some_name' ) is None
        assert not reg.listPredicates()
        self.assertRaises( KeyError, reg.removePredicate, 'xyzzy' )
    
    def test_reorder( self ):
        reg = self._makeOne()
        predIDs = ( 'foo', 'bar', 'baz', 'qux' )
        for predID in predIDs:
            reg.addPredicate( predID, 'name_suffix' )
        ids = tuple( map( lambda x: x[0], reg.listPredicates() ) )
        assert ids == predIDs
        reg.reorderPredicate( 'bar', 3 )
        ids = tuple( map( lambda x: x[0], reg.listPredicates() ) )
        assert ids == ( 'foo', 'baz', 'qux', 'bar' )

    def test_lookup( self ):

        reg = self._makeOne()
        reg.addPredicate( 'view', 'name_suffix' )
        reg.getPredicate( 'view' ).edit( skin_name_suffix='_view' )
        reg.assignCacheManagerID( 'view', 'View' )
        reg.addPredicate( 'form', 'name_suffix' )
        reg.getPredicate( 'form' ).edit( skin_name_suffix='_form' )
        reg.assignCacheManagerID( 'form', 'Form' )

        self.assertEqual( reg.findCacheManagerID( None, 'foo_view' ), 'View' )
        self.assertEqual( reg.findCacheManagerID( None, 'foo_form' ), 'Form' )
        self.assertEqual( reg.findCacheManagerID( None, 'some_name' ), None )

        reg.addPredicate( 'default', 'default' )
        reg.assignCacheManagerID( 'default', 'Default' )

        self.assertEqual( reg.findCacheManagerID( None, 'some_name' )
                        , 'Default' )

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( DefaultPredicateTests ) )
    suite.addTest( unittest.makeSuite( NameSuffixPredicateTests ) )
    suite.addTest( unittest.makeSuite( CachingToolRegistryTests ) )
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()

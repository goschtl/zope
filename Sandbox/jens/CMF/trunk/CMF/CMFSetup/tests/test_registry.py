""" Registry unit tests.

$Id$
"""
import unittest
import os

from Products.CMFSetup.tests.common import BaseRegistryTests

#==============================================================================
#   Dummy handlers
#==============================================================================
def ONE_FUNC( context ): pass
def TWO_FUNC( context ): pass
def THREE_FUNC( context ): pass
def FOUR_FUNC( context ): pass

ONE_FUNC_NAME = '%s.%s' % ( __name__, ONE_FUNC.__name__ )
TWO_FUNC_NAME = '%s.%s' % ( __name__, TWO_FUNC.__name__ )
THREE_FUNC_NAME = '%s.%s' % ( __name__, THREE_FUNC.__name__ )
FOUR_FUNC_NAME = '%s.%s' % ( __name__, FOUR_FUNC.__name__ )


#==============================================================================
#   SSR tests
#==============================================================================
class SetupStepRegistryTests( BaseRegistryTests ):

    def _getTargetClass( self ):

        from Products.CMFSetup.registry import SetupStepRegistry
        return SetupStepRegistry

    def test_empty( self ):

        registry = self._makeOne()

        self.assertEqual( len( registry.listSteps() ), 0 )
        self.assertEqual( len( registry.listStepMetadata() ), 0 )
        self.assertEqual( len( registry.sortSteps() ), 0 )

    def test_getStep_nonesuch( self ):

        registry = self._makeOne()

        self.assertEqual( registry.getStep( 'nonesuch' ), None )
        self.assertEqual( registry.getStep( 'nonesuch' ), None )
        default = object()
        self.failUnless( registry.getStepMetadata( 'nonesuch'
                                                 , default ) is default )
        self.failUnless( registry.getStep( 'nonesuch', default ) is default )
        self.failUnless( registry.getStepMetadata( 'nonesuch'
                                                 , default ) is default )

    def test_getStep_defaulted( self ):

        registry = self._makeOne()
        default = object()

        self.failUnless( registry.getStep( 'nonesuch', default ) is default )
        self.assertEqual( registry.getStepMetadata( 'nonesuch', {} ), {} )

    def test_registerStep_docstring( self ):

        def func_with_doc( site ):
            """This is the first line.

            This is the second line.
            """
        FUNC_NAME = '%s.%s' % ( __name__, func_with_doc.__name__ )

        registry = self._makeOne()

        registry.registerStep( id='docstring'
                             , version='1'
                             , handler=func_with_doc
                             , dependencies=()
                             )

        info = registry.getStepMetadata( 'docstring' )
        self.assertEqual( info[ 'id' ], 'docstring' )
        self.assertEqual( info[ 'handler' ], FUNC_NAME )
        self.assertEqual( info[ 'dependencies' ], () )
        self.assertEqual( info[ 'title' ], 'This is the first line.' )
        self.assertEqual( info[ 'description' ] , 'This is the second line.' )

    def test_registerStep_docstring_override( self ):

        def func_with_doc( site ):
            """This is the first line.

            This is the second line.
            """
        FUNC_NAME = '%s.%s' % ( __name__, func_with_doc.__name__ )

        registry = self._makeOne()

        registry.registerStep( id='docstring'
                             , version='1'
                             , handler=func_with_doc
                             , dependencies=()
                             , title='Title'
                             )

        info = registry.getStepMetadata( 'docstring' )
        self.assertEqual( info[ 'id' ], 'docstring' )
        self.assertEqual( info[ 'handler' ], FUNC_NAME )
        self.assertEqual( info[ 'dependencies' ], () )
        self.assertEqual( info[ 'title' ], 'Title' )
        self.assertEqual( info[ 'description' ] , 'This is the second line.' )

    def test_registerStep_single( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=( 'two', 'three' )
                             , title='One Step'
                             , description='One small step'
                             )

        steps = registry.listSteps()
        self.assertEqual( len( steps ), 1 )
        self.failUnless( 'one' in steps )

        sorted = registry.sortSteps()
        self.assertEqual( len( sorted ), 1 )
        self.assertEqual( sorted[ 0 ], 'one' )

        self.assertEqual( registry.getStep( 'one' ), ONE_FUNC )

        info = registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'version' ], '1' )
        self.assertEqual( info[ 'handler' ], ONE_FUNC_NAME )
        self.assertEqual( info[ 'dependencies' ], ( 'two', 'three' ) )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.assertEqual( info[ 'description' ], 'One small step' )

        info_list = registry.listStepMetadata()
        self.assertEqual( len( info_list ), 1 )
        self.assertEqual( info, info_list[ 0 ] )

    def test_registerStep_conflict( self ):

        registry = self._makeOne()

        registry.registerStep( id='one', version='1', handler=ONE_FUNC )

        self.assertRaises( KeyError
                         , registry.registerStep
                         , id='one'
                         , version='0'
                         , handler=ONE_FUNC
                         )

        self.assertRaises( KeyError
                         , registry.registerStep
                         , id='one'
                         , version='1'
                         , handler=ONE_FUNC
                         )

    def test_registerStep_replacement( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=( 'two', 'three' )
                             , title='One Step'
                             , description='One small step'
                             )

        registry.registerStep( id='one'
                             , version='1.1'
                             , handler=ONE_FUNC
                             , dependencies=()
                             , title='Leads to Another'
                             , description='Another small step'
                             )

        info = registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'version' ], '1.1' )
        self.assertEqual( info[ 'dependencies' ], () )
        self.assertEqual( info[ 'title' ], 'Leads to Another' )
        self.assertEqual( info[ 'description' ], 'Another small step' )

    def test_registerStep_multiple( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=()
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , handler=TWO_FUNC
                             , dependencies=()
                             )

        registry.registerStep( id='three'
                             , version='3'
                             , handler=THREE_FUNC
                             , dependencies=()
                             )

        steps = registry.listSteps()
        self.assertEqual( len( steps ), 3 )
        self.failUnless( 'one' in steps )
        self.failUnless( 'two' in steps )
        self.failUnless( 'three' in steps )

    def test_sortStep_simple( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=( 'two', )
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , handler=TWO_FUNC
                             , dependencies=()
                             )

        steps = registry.sortSteps()
        self.assertEqual( len( steps ), 2 )
        one = steps.index( 'one' )
        two = steps.index( 'two' )

        self.failUnless( 0 <= two < one )

    def test_sortStep_chained( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=( 'two', )
                             , title='One small step'
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , handler=TWO_FUNC
                             , dependencies=( 'three', )
                             , title='Texas two step'
                             )

        registry.registerStep( id='three'
                             , version='3'
                             , handler=THREE_FUNC
                             , dependencies=()
                             , title='Gimme three steps'
                             )

        steps = registry.sortSteps()
        self.assertEqual( len( steps ), 3 )
        one = steps.index( 'one' )
        two = steps.index( 'two' )
        three = steps.index( 'three' )

        self.failUnless( 0 <= three < two < one )

    def test_sortStep_complex( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=( 'two', )
                             , title='One small step'
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , handler=TWO_FUNC
                             , dependencies=( 'four', )
                             , title='Texas two step'
                             )

        registry.registerStep( id='three'
                             , version='3'
                             , handler=THREE_FUNC
                             , dependencies=( 'four', )
                             , title='Gimme three steps'
                             )

        registry.registerStep( id='four'
                             , version='4'
                             , handler=FOUR_FUNC
                             , dependencies=()
                             , title='Four step program'
                             )

        steps = registry.sortSteps()
        self.assertEqual( len( steps ), 4 )
        one = steps.index( 'one' )
        two = steps.index( 'two' )
        three = steps.index( 'three' )
        four = steps.index( 'four' )

        self.failUnless( 0 <= four < two < one )
        self.failUnless( 0 <= four < three )

    def test_sortStep_equivalence( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=( 'two', 'three' )
                             , title='One small step'
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , handler=TWO_FUNC
                             , dependencies=( 'four', )
                             , title='Texas two step'
                             )

        registry.registerStep( id='three'
                             , version='3'
                             , handler=THREE_FUNC
                             , dependencies=( 'four', )
                             , title='Gimme three steps'
                             )

        registry.registerStep( id='four'
                             , version='4'
                             , handler=FOUR_FUNC
                             , dependencies=()
                             , title='Four step program'
                             )

        steps = registry.sortSteps()
        self.assertEqual( len( steps ), 4 )
        one = steps.index( 'one' )
        two = steps.index( 'two' )
        three = steps.index( 'three' )
        four = steps.index( 'four' )

        self.failUnless( 0 <= four < two < one )
        self.failUnless( 0 <= four < three < one )

    def test_checkComplete_simple( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=( 'two', )
                             )

        incomplete = registry.checkComplete()
        self.assertEqual( len( incomplete ), 1 )
        self.failUnless( ( 'one', 'two' ) in incomplete )

        registry.registerStep( id='two'
                             , version='2'
                             , handler=TWO_FUNC
                             , dependencies=()
                             )

        self.assertEqual( len( registry.checkComplete() ), 0 )

    def test_checkComplete_double( self ):

        registry = self._makeOne()

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=( 'two', 'three' )
                             )

        incomplete = registry.checkComplete()
        self.assertEqual( len( incomplete ), 2 )
        self.failUnless( ( 'one', 'two' ) in incomplete )
        self.failUnless( ( 'one', 'three' ) in incomplete )

        registry.registerStep( id='two'
                             , version='2'
                             , handler=TWO_FUNC
                             , dependencies=()
                             )

        incomplete = registry.checkComplete()
        self.assertEqual( len( incomplete ), 1 )
        self.failUnless( ( 'one', 'three' ) in incomplete )

        registry.registerStep( id='three'
                             , version='3'
                             , handler=THREE_FUNC
                             , dependencies=()
                             )

        self.assertEqual( len( registry.checkComplete() ), 0 )

        registry.registerStep( id='two'
                             , version='2.1'
                             , handler=TWO_FUNC
                             , dependencies=( 'four', )
                             )

        incomplete = registry.checkComplete()
        self.assertEqual( len( incomplete ), 1 )
        self.failUnless( ( 'two', 'four' ) in incomplete )

    def test_export_empty( self ):

        registry = self._makeOne().__of__( self.root )

        xml = registry.exportAsXML()

        self._compareDOM( registry.exportAsXML(), _EMPTY_STEPS_EXPORT )

    def test_export_single( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=()
                             , title='One Step'
                             , description='One small step'
                             )

        self._compareDOM( registry.exportAsXML(), _SINGLE_STEP_EXPORT )

    def test_export_ordered( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=( 'two', )
                             , title='One Step'
                             , description='One small step'
                             )

        registry.registerStep( id='two'
                             , version='2'
                             , handler=TWO_FUNC
                             , dependencies=( 'three', )
                             , title='Two Steps'
                             , description='Texas two step'
                             )

        registry.registerStep( id='three'
                             , version='3'
                             , handler=THREE_FUNC
                             , dependencies=()
                             , title='Three Steps'
                             , description='Gimme three steps'
                             )

        self._compareDOM( registry.exportAsXML(), _ORDERED_STEPS_EXPORT )

    def test_import_empty( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerStep( id='one'
                             , version='1'
                             , handler=ONE_FUNC
                             , dependencies=()
                             , description='One small step'
                             )

        registry.importFromXML( _EMPTY_STEPS_EXPORT )

        self.assertEqual( len( registry.listSteps() ), 0 )
        self.assertEqual( len( registry.listStepMetadata() ), 0 )
        self.assertEqual( len( registry.sortSteps() ), 0 )

    def test_import_single( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerStep( id='two'
                             , version='2'
                             , handler=TWO_FUNC
                             , dependencies=()
                             , title='Two Steps'
                             , description='Texas two step'
                             )

        registry.importFromXML( _SINGLE_STEP_EXPORT )

        self.assertEqual( len( registry.listSteps() ), 1 )
        self.failUnless( 'one' in registry.listSteps() )

        info = registry.getStepMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'version' ], '1' )
        self.assertEqual( info[ 'handler' ], ONE_FUNC_NAME )
        self.assertEqual( info[ 'dependencies' ], () )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.failUnless( 'One small step' in info[ 'description' ] )

    def test_import_ordered( self ):

        registry = self._makeOne().__of__( self.root )

        registry.importFromXML( _ORDERED_STEPS_EXPORT )

        self.assertEqual( len( registry.listSteps() ), 3 )
        self.failUnless( 'one' in registry.listSteps() )
        self.failUnless( 'two' in registry.listSteps() )
        self.failUnless( 'three' in registry.listSteps() )

        steps = registry.sortSteps()
        self.assertEqual( len( steps ), 3 )
        one = steps.index( 'one' )
        two = steps.index( 'two' )
        three = steps.index( 'three' )

        self.failUnless( 0 <= three < two < one )


_EMPTY_STEPS_EXPORT = """\
<?xml version="1.0"?>
<setup-steps>
</setup-steps>
"""

_SINGLE_STEP_EXPORT = """\
<?xml version="1.0"?>
<setup-steps>
 <setup-step id="one"
             version="1"
             handler="%s"
             title="One Step">
  One small step
 </setup-step>
</setup-steps>
""" % ( ONE_FUNC_NAME, )

_ORDERED_STEPS_EXPORT = """\
<?xml version="1.0"?>
<setup-steps>
 <setup-step id="one"
             version="1"
             handler="%s"
             title="One Step">
  <dependency step="two" />
  One small step
 </setup-step>
 <setup-step id="three"
             version="3"
             handler="%s"
             title="Three Steps">
  Gimme three steps
 </setup-step>
 <setup-step id="two"
             version="2"
             handler="%s"
             title="Two Steps">
  <dependency step="three" />
  Texas two step
 </setup-step>
</setup-steps>
""" % ( ONE_FUNC_NAME, THREE_FUNC_NAME, TWO_FUNC_NAME )


#==============================================================================
#   ESR tests
#==============================================================================
class ExportScriptRegistryTests( BaseRegistryTests ):

    def _getTargetClass( self ):

        from Products.CMFSetup.registry import ExportScriptRegistry
        return ExportScriptRegistry

    def _makeOne( self, *args, **kw ):

        return self._getTargetClass()( *args, **kw )

    def test_empty( self ):

        registry = self._makeOne()
        self.assertEqual( len( registry.listScripts() ), 0 )
        self.assertEqual( len( registry.listScriptMetadata() ), 0 )

    def test_getScript_nonesuch( self ):

        registry = self._makeOne()
        self.assertEqual( registry.getScript( 'nonesuch' ), None )

    def test_getScript_defaulted( self ):

        registry = self._makeOne()
        default = lambda x: false
        self.assertEqual( registry.getScript( 'nonesuch', default ), default )

    def test_getScriptMetadata_nonesuch( self ):

        registry = self._makeOne()
        self.assertEqual( registry.getScriptMetadata( 'nonesuch' ), None )

    def test_getScriptMetadata_defaulted( self ):

        registry = self._makeOne()
        self.assertEqual( registry.getScriptMetadata( 'nonesuch', {} ), {} )

    def test_registerScript_simple( self ):

        registry = self._makeOne()
        registry.registerScript( 'one', ONE_FUNC )
        info = registry.getScriptMetadata( 'one', {} )

        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'handler' ], ONE_FUNC_NAME )
        self.assertEqual( info[ 'title' ], 'one' )
        self.assertEqual( info[ 'description' ], '' )

    def test_registerScript_docstring( self ):

        def func_with_doc( site ):
            """This is the first line.

            This is the second line.
            """
        FUNC_NAME = '%s.%s' % ( __name__, func_with_doc.__name__ )

        registry = self._makeOne()
        registry.registerScript( 'one', func_with_doc )
        info = registry.getScriptMetadata( 'one', {} )

        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'handler' ], FUNC_NAME )
        self.assertEqual( info[ 'title' ], 'This is the first line.' )
        self.assertEqual( info[ 'description' ] , 'This is the second line.' )

    def test_registerScript_docstring_with_override( self ):

        def func_with_doc( site ):
            """This is the first line.

            This is the second line.
            """
        FUNC_NAME = '%s.%s' % ( __name__, func_with_doc.__name__ )

        registry = self._makeOne()
        registry.registerScript( 'one', func_with_doc
                               , description='Description' )
        info = registry.getScriptMetadata( 'one', {} )

        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'handler' ], FUNC_NAME )
        self.assertEqual( info[ 'title' ], 'This is the first line.' )
        self.assertEqual( info[ 'description' ], 'Description' )

    def test_registerScript_collision( self ):

        registry = self._makeOne()
        registry.registerScript( 'one', ONE_FUNC )
        self.assertRaises( KeyError, registry.registerScript, 'one', TWO_FUNC )

    def test_export_empty( self ):

        registry = self._makeOne().__of__( self.root )

        xml = registry.exportAsXML()

        self._compareDOM( registry.exportAsXML(), _EMPTY_SCRIPTS_EXPORT )

    def test_export_single( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerScript( id='one'
                               , handler=ONE_FUNC
                               , title='One Step'
                               , description='One small step'
                               )

        self._compareDOM( registry.exportAsXML(), _SINGLE_SCRIPT_EXPORT )

    def test_export_ordered( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerScript( id='one'
                               , handler=ONE_FUNC
                               , title='One Step'
                               , description='One small step'
                               )

        registry.registerScript( id='two'
                               , handler=TWO_FUNC
                               , title='Two Steps'
                               , description='Texas two step'
                               )

        registry.registerScript( id='three'
                               , handler=THREE_FUNC
                               , title='Three Steps'
                               , description='Gimme three steps'
                               )

        self._compareDOM( registry.exportAsXML(), _ORDERED_SCRIPTS_EXPORT )

    def test_import_empty( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerScript( id='one'
                               , handler=ONE_FUNC
                               , description='One small step'
                               )

        registry.importFromXML( _EMPTY_SCRIPTS_EXPORT )

        self.assertEqual( len( registry.listScripts() ), 0 )
        self.assertEqual( len( registry.listScriptMetadata() ), 0 )

    def test_import_single( self ):

        registry = self._makeOne().__of__( self.root )

        registry.registerScript( id='two'
                               , handler=TWO_FUNC
                               , title='Two Steps'
                               , description='Texas two step'
                               )

        registry.importFromXML( _SINGLE_SCRIPT_EXPORT )

        self.assertEqual( len( registry.listScripts() ), 1 )
        self.failUnless( 'one' in registry.listScripts() )

        info = registry.getScriptMetadata( 'one' )
        self.assertEqual( info[ 'id' ], 'one' )
        self.assertEqual( info[ 'handler' ], ONE_FUNC_NAME )
        self.assertEqual( info[ 'title' ], 'One Step' )
        self.failUnless( 'One small step' in info[ 'description' ] )

    def test_import_ordered( self ):

        registry = self._makeOne().__of__( self.root )

        registry.importFromXML( _ORDERED_SCRIPTS_EXPORT )

        self.assertEqual( len( registry.listScripts() ), 3 )
        self.failUnless( 'one' in registry.listScripts() )
        self.failUnless( 'two' in registry.listScripts() )
        self.failUnless( 'three' in registry.listScripts() )


_EMPTY_SCRIPTS_EXPORT = """\
<?xml version="1.0"?>
<export-scripts>
</export-scripts>
"""

_SINGLE_SCRIPT_EXPORT = """\
<?xml version="1.0"?>
<export-scripts>
 <export-script id="one"
                handler="%s"
                title="One Step">
  One small step
 </export-script>
</export-scripts>
""" % ( ONE_FUNC_NAME, )

_ORDERED_SCRIPTS_EXPORT = """\
<?xml version="1.0"?>
<export-scripts>
 <export-script id="one"
                handler="%s"
                title="One Step">
  One small step
 </export-script>
 <export-script id="three"
                handler="%s"
                title="Three Steps">
  Gimme three steps
 </export-script>
 <export-script id="two"
                handler="%s"
                title="Two Steps">
  Texas two step
 </export-script>
</export-scripts>
""" % ( ONE_FUNC_NAME, THREE_FUNC_NAME, TWO_FUNC_NAME )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( SetupStepRegistryTests ),
        unittest.makeSuite( ExportScriptRegistryTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

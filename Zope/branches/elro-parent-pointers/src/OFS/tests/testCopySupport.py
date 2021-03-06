import unittest

import cStringIO

import transaction
from AccessControl import SecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
from Acquisition import Implicit
from OFS.Application import Application
from OFS.Folder import manage_addFolder
from OFS.Image import manage_addFile
from Testing.makerequest import newrequest
from zope import component
from zope.testing import cleanup
from persistent import Persistent
from zope.globalrequest import setRequest
from zope.location import Location


ADD_IMAGES_AND_FILES = 'Add images and files'
FILE_META_TYPES = ( { 'name'        : 'File'
                    , 'action'      : 'manage_addFile'
                    , 'permission'  : ADD_IMAGES_AND_FILES
                    }
                  ,
                  )

class UnitTestSecurityPolicy:
    """
        Stub out the existing security policy for unit testing purposes.
    """
    #
    #   Standard SecurityPolicy interface
    #
    def validate( self
                , accessed=None
                , container=None
                , name=None
                , value=None
                , context=None
                , roles=None
                , *args
                , **kw):
        return 1

    def checkPermission( self, permission, object, context) :
        return 1

class UnitTestUser( Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    def getId( self ):
        return 'unit_tester'

    getUserName = getId

    def allowed( self, object, object_roles=None ):
        return 1

def makeConnection():
    import ZODB
    from ZODB.DemoStorage import DemoStorage

    s = DemoStorage()
    return ZODB.DB( s ).open()


class PersistentLocation(Persistent, Location):
    pass


class CopySupportTestBase(unittest.TestCase):

    def _initFolders(self):

        self.connection = makeConnection()
        try:
            r = self.connection.root()
            a = Application()
            r['Application'] = a
            self.root = a
            responseOut = self.responseOut = cStringIO.StringIO()
            request = newrequest(stdout=responseOut)
            setRequest(request)
            self.app =  a
            manage_addFolder( self.app, 'folder1' )
            manage_addFolder( self.app, 'folder2' )
            folder1 = getattr( self.app, 'folder1' )
            folder2 = getattr( self.app, 'folder2' )

            manage_addFile( folder1, 'file'
                          , file='', content_type='text/plain')

            # Hack, we need a _p_mtime for the file, so we make sure that it
            # has one. We use a subtransaction, which means we can rollback
            # later and pretend we didn't touch the ZODB.
            transaction.commit()
        except:
            self.connection.close()
            raise
        transaction.begin()

        return self.app._getOb( 'folder1' ), self.app._getOb( 'folder2' )

    def _cleanApp( self ):

        transaction.abort()
        self.app._p_jar.sync()
        self.connection.close()
        del self.app
        del self.responseOut
        del self.root
        del self.connection
        setRequest(None)
        cleanup.cleanUp()


class TestCopySupport( CopySupportTestBase ):

    def setUp( self ):
        from zope.copy.interfaces import ICopyHook
        from zope.location.interfaces import ILocation
        from zope.location.pickling import LocationCopyHook
        component.provideAdapter(LocationCopyHook, (ILocation,), ICopyHook)

        folder1, folder2 = self._initFolders()

        folder1.all_meta_types = folder2.all_meta_types = FILE_META_TYPES

        self.folder1 = folder1
        self.folder2 = folder2

        self.policy = UnitTestSecurityPolicy()
        self.oldPolicy = SecurityManager.setSecurityPolicy( self.policy )
        newSecurityManager( None, UnitTestUser().__of__( self.root ) )

    def tearDown( self ):

        noSecurityManager()
        SecurityManager.setSecurityPolicy( self.oldPolicy )
        del self.oldPolicy
        del self.policy
        del self.folder2
        del self.folder1

        self._cleanApp()

    def test_interfaces(self):
        from OFS.CopySupport import CopyContainer
        from OFS.CopySupport import CopySource
        from OFS.interfaces import ICopyContainer
        from OFS.interfaces import ICopySource
        from zope.interface.verify import verifyClass

        verifyClass(ICopyContainer, CopyContainer)
        verifyClass(ICopySource, CopySource)

    def testRename( self ):
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.folder1.manage_renameObject( id='file', new_id='filex' )
        self.assertFalse( 'file' in self.folder1.objectIds() )
        self.assertTrue( 'filex' in self.folder1.objectIds() )

    def testCopy( self ):
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertFalse( 'file' in self.folder2.objectIds() )
        cookie = self.folder1.manage_copyObjects( ids=('file',) )
        self.folder2.manage_pasteObjects( cookie )
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertTrue( 'file' in self.folder2.objectIds() )
        self.assertTrue(self.folder2.file.__parent__ is self.folder2)

    def testCut( self ):
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertFalse( 'file' in self.folder2.objectIds() )
        cookie = self.folder1.manage_cutObjects( ids=('file',) )
        self.folder2.manage_pasteObjects( cookie )
        self.assertFalse( 'file' in self.folder1.objectIds() )
        self.assertTrue( 'file' in self.folder2.objectIds() )

    def testCopyNewObject(self):
        self.assertFalse('newfile' in self.folder1.objectIds())
        manage_addFile(self.folder1, 'newfile',
                       file='', content_type='text/plain')
        cookie = self.folder1.manage_copyObjects(ids=('newfile',))
        self.folder2.manage_pasteObjects(cookie)
        self.assertTrue('newfile' in self.folder1.objectIds())
        self.assertTrue('newfile' in self.folder2.objectIds())
    
    def testCopyExcludesNoncontainedObjects(self):
        self.app.other_ob = other_ob = PersistentLocation()
        self.app.other_ob.__parent__ = self.app

        ob = self.folder1.file
        ob.other_ob = self.app.other_ob
        copied_ob = ob._getCopy(self.folder1)
        self.assertTrue(copied_ob.other_ob is other_ob)

    def testPasteSingleNotSameID( self ):
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertFalse( 'file' in self.folder2.objectIds() )
        cookie = self.folder1.manage_copyObjects( ids=('file',) )
        result = self.folder2.manage_pasteObjects( cookie )
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertTrue( 'file' in self.folder2.objectIds() )
        self.assertTrue( result == [{'id':'file', 'new_id':'file'}])

    def testPasteSingleSameID( self ):
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertFalse( 'file' in self.folder2.objectIds() )
        manage_addFile(self.folder2, 'file',
                       file='', content_type='text/plain')
        cookie = self.folder1.manage_copyObjects( ids=('file',) )
        result = self.folder2.manage_pasteObjects( cookie )
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertTrue( 'file' in self.folder2.objectIds() )
        self.assertTrue( 'copy_of_file' in self.folder2.objectIds() )
        self.assertTrue( result == [{'id':'file', 'new_id':'copy_of_file'}])

    def testPasteSingleSameIDMultipleTimes(self):
        cookie = self.folder1.manage_copyObjects(ids=('file',))
        result = self.folder1.manage_pasteObjects(cookie)
        self.assertEqual(self.folder1.objectIds(), ['file', 'copy_of_file'])
        self.assertEqual(result, [{'id':'file', 'new_id':'copy_of_file'}])
        # make another copy of file
        cookie = self.folder1.manage_copyObjects(ids=('file',))
        result = self.folder1.manage_pasteObjects(cookie)
        self.assertEqual(self.folder1.objectIds(),
                         ['file', 'copy_of_file', 'copy2_of_file'])
        self.assertEqual(result, [{'id':'file', 'new_id':'copy2_of_file'}])
        # now copy the copy
        cookie = self.folder1.manage_copyObjects(ids=('copy_of_file',))
        result = self.folder1.manage_pasteObjects(cookie)
        self.assertEqual(self.folder1.objectIds(),
                         ['file', 'copy_of_file', 'copy2_of_file',
                         'copy3_of_file'])
        self.assertEqual(result, [{'id':'copy_of_file',
                                   'new_id':'copy3_of_file'}])
        # or copy another copy
        cookie = self.folder1.manage_copyObjects(ids=('copy2_of_file',))
        result = self.folder1.manage_pasteObjects(cookie)
        self.assertEqual(self.folder1.objectIds(),
                         ['file', 'copy_of_file', 'copy2_of_file',
                         'copy3_of_file', 'copy4_of_file'])
        self.assertEqual(result, [{'id':'copy2_of_file',
                                   'new_id':'copy4_of_file'}])

    def testPasteSpecialName(self):
        manage_addFile(self.folder1, 'copy_of_',
                       file='', content_type='text/plain')
        cookie = self.folder1.manage_copyObjects(ids=('copy_of_',))
        result = self.folder1.manage_pasteObjects(cookie)
        self.assertEqual(self.folder1.objectIds(),
                         ['file', 'copy_of_', 'copy2_of_'])
        self.assertEqual(result, [{'id':'copy_of_', 'new_id':'copy2_of_'}])

    def testPasteMultiNotSameID( self ):
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertFalse( 'file1' in self.folder1.objectIds() )
        manage_addFile(self.folder1, 'file1',
                       file='', content_type='text/plain')
        self.assertFalse( 'file2' in self.folder1.objectIds() )
        manage_addFile(self.folder1, 'file2',
                       file='', content_type='text/plain')
        self.assertFalse( 'file' in self.folder2.objectIds() )
        self.assertFalse( 'file1' in self.folder2.objectIds() )
        self.assertFalse( 'file2' in self.folder2.objectIds() )
        cookie = self.folder1.manage_copyObjects( ids=('file','file1','file2',) )
        result = self.folder2.manage_pasteObjects( cookie )
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertTrue( 'file1' in self.folder1.objectIds() )
        self.assertTrue( 'file2' in self.folder1.objectIds() )
        self.assertTrue( 'file' in self.folder2.objectIds() )
        self.assertTrue( 'file1' in self.folder2.objectIds() )
        self.assertTrue( 'file2' in self.folder2.objectIds() )
        self.assertTrue( result == [{'id':'file', 'new_id':'file'},
                                    {'id':'file1', 'new_id':'file1'},
                                    {'id':'file2', 'new_id':'file2'}])

    def testPasteMultiSameID( self ):
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertFalse( 'file1' in self.folder1.objectIds() )
        manage_addFile(self.folder1, 'file1',
                       file='', content_type='text/plain')
        self.assertFalse( 'file2' in self.folder1.objectIds() )
        manage_addFile(self.folder1, 'file2',
                       file='', content_type='text/plain')
        self.assertFalse( 'file' in self.folder2.objectIds() )
        manage_addFile(self.folder2, 'file',
                       file='', content_type='text/plain')
        self.assertFalse( 'file1' in self.folder2.objectIds() )
        manage_addFile(self.folder2, 'file1',
                       file='', content_type='text/plain')
        self.assertFalse( 'file2' in self.folder2.objectIds() )
        manage_addFile(self.folder2, 'file2',
                       file='', content_type='text/plain')
        cookie = self.folder1.manage_copyObjects( ids=('file','file1','file2',) )
        result = self.folder2.manage_pasteObjects( cookie )
        self.assertTrue( 'file' in self.folder1.objectIds() )
        self.assertTrue( 'file1' in self.folder1.objectIds() )
        self.assertTrue( 'file2' in self.folder1.objectIds() )
        self.assertTrue( 'file' in self.folder2.objectIds() )
        self.assertTrue( 'file1' in self.folder2.objectIds() )
        self.assertTrue( 'file2' in self.folder2.objectIds() )
        self.assertTrue( 'copy_of_file' in self.folder2.objectIds() )
        self.assertTrue( 'copy_of_file1' in self.folder2.objectIds() )
        self.assertTrue( 'copy_of_file2' in self.folder2.objectIds() )
        self.assertTrue( result == [{'id':'file', 'new_id':'copy_of_file'},
                                    {'id':'file1', 'new_id':'copy_of_file1'},
                                    {'id':'file2', 'new_id':'copy_of_file2'}])

class _SensitiveSecurityPolicy:

    def __init__( self, validate_lambda, checkPermission_lambda ):
        self._lambdas = ( validate_lambda, checkPermission_lambda )

    def validate( self, *args, **kw ):
        from zExceptions import Unauthorized

        allowed = self._lambdas[ 0 ]( *args, **kw )
        if not allowed:
            raise Unauthorized
        return 1

    def checkPermission( self, *args, **kw ) :
        return self._lambdas[ 1 ]( *args, **kw )

class _AllowedUser( UnitTestUser ):

    def __init__( self, allowed_lambda ):
        self._lambdas = ( allowed_lambda, )

    def allowed( self, object, object_roles=None ):
        return self._lambdas[ 0 ]( object, object_roles )

class TestCopySupportSecurity( CopySupportTestBase ):

    _old_policy = None

    def setUp( self ):
        self._scrubSecurity()

    def tearDown( self ):

        self._scrubSecurity()
        self._cleanApp()

    def _scrubSecurity( self ):

        noSecurityManager()

        if self._old_policy is not None:
            SecurityManager.setSecurityPolicy( self._old_policy )

    def _assertCopyErrorUnauth( self, callable, *args, **kw ):

        import re
        from zExceptions import Unauthorized
        from OFS.CopySupport import CopyError

        ce_regex = kw.get( 'ce_regex' )
        if ce_regex is not None:
            del kw[ 'ce_regex' ]

        try:
            callable( *args, **kw )

        except CopyError, e:

            if ce_regex is not None:

                pattern = re.compile( ce_regex, re.DOTALL )
                if pattern.search( e.args[0] ) is None:
                    self.fail( "Paste failed; didn't match pattern:\n%s" % e )

            else:
                self.fail( "Paste failed; no pattern:\n%s" % e )

        except Unauthorized, e:
            pass

        else:
            self.fail( "Paste allowed unexpectedly." )

    def _initPolicyAndUser( self
                          , a_lambda=None
                          , v_lambda=None
                          , c_lambda=None
                          ):
        def _promiscuous( *args, **kw ):
            return 1

        if a_lambda is None:
            a_lambda = _promiscuous

        if v_lambda is None:
            v_lambda = _promiscuous

        if c_lambda is None:
            c_lambda = _promiscuous

        scp = _SensitiveSecurityPolicy( v_lambda, c_lambda )
        self._old_policy = SecurityManager.setSecurityPolicy( scp )

        newSecurityManager( None
                          , _AllowedUser( a_lambda ).__of__( self.root ) )

    def test_copy_baseline( self ):

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = FILE_META_TYPES

        self._initPolicyAndUser()

        self.assertTrue( 'file' in folder1.objectIds() )
        self.assertFalse( 'file' in folder2.objectIds() )

        cookie = folder1.manage_copyObjects( ids=( 'file', ) )
        folder2.manage_pasteObjects( cookie )

        self.assertTrue( 'file' in folder1.objectIds() )
        self.assertTrue( 'file' in folder2.objectIds() )

    def test_copy_cant_read_source( self ):

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = FILE_META_TYPES

        a_file = folder1._getOb( 'file' )

        def _validate( a, c, n, v, *args, **kw ):
            return aq_base( v ) is not aq_base( a_file )

        self._initPolicyAndUser( v_lambda=_validate )

        cookie = folder1.manage_copyObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Insufficient privileges'
                                   )

    def test_copy_cant_create_target_metatype_not_supported( self ):

        from OFS.CopySupport import CopyError

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = ()

        self._initPolicyAndUser()

        cookie = folder1.manage_copyObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Not Supported'
                                   )

    def test_move_baseline( self ):

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = FILE_META_TYPES

        self.assertTrue( 'file' in folder1.objectIds() )
        self.assertFalse( 'file' in folder2.objectIds() )

        self._initPolicyAndUser()

        cookie = folder1.manage_cutObjects( ids=( 'file', ) )
        folder2.manage_pasteObjects( cookie )

        self.assertFalse( 'file' in folder1.objectIds() )
        self.assertTrue( 'file' in folder2.objectIds() )

    def test_move_cant_read_source( self ):

        from OFS.CopySupport import CopyError

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = FILE_META_TYPES

        a_file = folder1._getOb( 'file' )

        def _validate( a, c, n, v, *args, **kw ):
            return aq_base( v ) is not aq_base( a_file )

        self._initPolicyAndUser( v_lambda=_validate )

        cookie = folder1.manage_cutObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Insufficient privileges'
                                   )

    def test_move_cant_create_target_metatype_not_supported( self ):

        from OFS.CopySupport import CopyError

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = ()

        self._initPolicyAndUser()

        cookie = folder1.manage_cutObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Not Supported'
                                   )

    def test_move_cant_create_target_metatype_not_allowed( self ):

        from OFS.CopySupport import CopyError

        folder1, folder2 = self._initFolders()
        folder2.all_meta_types = FILE_META_TYPES

        def _no_add_images_and_files(permission, object, context):
            return permission != ADD_IMAGES_AND_FILES

        self._initPolicyAndUser( c_lambda=_no_add_images_and_files )

        cookie = folder1.manage_cutObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Insufficient Privileges'
                                             + '.*%s' % ADD_IMAGES_AND_FILES
                                   )

    def test_move_cant_delete_source( self ):

        from OFS.CopySupport import CopyError
        from AccessControl.Permissions import delete_objects as DeleteObjects

        folder1, folder2 = self._initFolders()
        folder1.manage_permission( DeleteObjects, roles=(), acquire=0 )
        folder2.all_meta_types = FILE_META_TYPES

        def _no_delete_objects(permission, object, context):
            return permission != DeleteObjects

        self._initPolicyAndUser( c_lambda=_no_delete_objects )

        cookie = folder1.manage_cutObjects( ids=( 'file', ) )
        self._assertCopyErrorUnauth( folder2.manage_pasteObjects
                                   , cookie
                                   , ce_regex='Insufficient Privileges'
                                             + '.*%s' % DeleteObjects
                                   )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( TestCopySupport ) )
    suite.addTest( unittest.makeSuite( TestCopySupportSecurity ) )
    return suite

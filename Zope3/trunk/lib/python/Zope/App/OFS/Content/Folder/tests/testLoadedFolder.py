##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""

$Id: testLoadedFolder.py,v 1.2 2002/06/10 23:28:02 jim Exp $
"""

import unittest


class Test( unittest.TestCase ):


    def _makeFolder( self ):
        """ """
        from Zope.App.OFS.Content.Folder.LoadedFolder import LoadedFolder

        return LoadedFolder()
        


    def testEmpty( self ):

        folder = self._makeFolder()
        self.failIf( folder.keys()         )
        self.failIf( folder.values()      )
        self.failIf( folder.items()       )
        self.failIf( len(folder)       )
        self.failIf( 'foo' in folder)

        self.assertEquals( folder.get( 'foo', None ), None )
        self.assertRaises( KeyError, folder.__getitem__, 'foo' )

        self.assertRaises( KeyError, folder.__delitem__, 'foo' )

    def testOneItem( self ):

        folder = self._makeFolder()
        foo = []
        folder.setObject( 'foo', foo )

        self.assertEquals( len( folder.keys() ), 1             )
        self.assertEquals( folder.keys()[0], 'foo'             )
        self.assertEquals( len( folder.values() ), 1          )
        self.assertEquals( folder.values()[0], foo            )
        self.assertEquals( len( folder.items() ), 1           )
        self.assertEquals( folder.items()[0], ( 'foo', foo )  )
        self.assertEquals( len(folder), 1                  )

        self.failUnless('foo' in folder)
        self.failIf('bar' in folder)

        self.assertEquals( folder.get( 'foo', None ), foo )
        self.assertEquals( folder['foo'], foo )

        self.assertRaises( KeyError, folder.__getitem__, 'qux' )

        foo2 = []
        folder.setObject( 'foo', foo )

        self.assertEquals( len( folder.keys() ), 1             )
        self.assertEquals( folder.keys()[0], 'foo'             )
        self.assertEquals( len( folder.values() ), 1          )
        self.assertEquals( folder.values()[0], foo2           )
        self.assertEquals( len( folder.items() ), 1           )
        self.assertEquals( folder.items()[0], ( 'foo', foo2 ) )
        self.assertEquals( len(folder), 1                  )

        del folder['foo']

        self.failIf( folder.keys()         )
        self.failIf( folder.values()      )
        self.failIf( folder.items()       )
        self.failIf( len(folder)       )
        self.failIf('foo' in folder)

        self.assertRaises( KeyError, folder.__getitem__, 'foo' )
        self.assertEquals( folder.get( 'foo', None ), None )
        self.assertRaises( KeyError, folder.__delitem__, 'foo' )

    def testManyItems( self ):

        folder = self._makeFolder()
        objects = [ [0], [1], [2], [3] ]
        folder.setObject( 'foo', objects[0] )
        folder.setObject( 'bar', objects[1] )
        folder.setObject( 'baz', objects[2] )
        folder.setObject( 'bam', objects[3] )

        self.assertEquals( len( folder.keys() ), len( objects ) )
        self.failUnless( 'foo' in folder.keys() )
        self.failUnless( 'bar' in folder.keys() )
        self.failUnless( 'baz' in folder.keys() )
        self.failUnless( 'bam' in folder.keys() )

        self.assertEquals( len( folder.values() ), len( objects ) )
        self.failUnless( objects[0] in folder.values() )
        self.failUnless( objects[1] in folder.values() )
        self.failUnless( objects[2] in folder.values() )
        self.failUnless( objects[3] in folder.values() )

        self.assertEquals( len( folder.items() ), len( objects ) )
        self.failUnless( ( 'foo', objects[0] ) in folder.items() )
        self.failUnless( ( 'bar', objects[1] ) in folder.items() )
        self.failUnless( ( 'baz', objects[2] ) in folder.items() )
        self.failUnless( ( 'bam', objects[3] ) in folder.items() )

        self.assertEquals( len(folder), len( objects ) )

        self.failUnless('foo' in folder)
        self.failUnless('bar' in folder)
        self.failUnless('baz' in folder)
        self.failUnless('bam' in folder)
        self.failIf('qux' in folder)

        self.assertEquals( folder.get( 'foo', None ), objects[0] )
        self.assertEquals( folder['foo'],       objects[0] )
        self.assertEquals( folder.get( 'bar', None ), objects[1] )
        self.assertEquals( folder['bar'],       objects[1] )
        self.assertEquals( folder.get( 'baz', None ), objects[2] )
        self.assertEquals( folder['baz'],       objects[2] )
        self.assertEquals( folder.get( 'bam', None ), objects[3] )
        self.assertEquals( folder['bam'],       objects[3] )

        self.assertEquals( folder.get( 'qux', None ), None )
        self.assertRaises( KeyError, folder.__getitem__, 'qux' )

        del folder['foo']
        self.assertEquals( len(folder), len( objects ) - 1 )
        self.failIf( 'foo' in folder)
        self.failIf( 'foo' in folder.keys() )

        self.failIf( objects[0] in folder.values() )
        self.failIf( ( 'foo', objects[0] ) in folder.items() )

        self.assertEquals( folder.get( 'foo', None ), None )
        self.assertRaises( KeyError, folder.__getitem__, 'foo' )

        self.assertRaises( KeyError, folder.__delitem__, 'foo' )

        del folder['bar']
        del folder['baz']
        del folder['bam']

        self.failIf( folder.keys()         )
        self.failIf( folder.values()      )
        self.failIf( folder.items()       )
        self.failIf( len(folder)       )
        self.failIf('foo' in folder)
        self.failIf('bar' in folder)
        self.failIf('baz' in folder)
        self.failIf('bam' in folder)



def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )

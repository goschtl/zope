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

$Id: testFile.py,v 1.2 2002/06/10 23:28:00 jim Exp $
"""

import unittest, ZODB
from Interface.Verify import verifyClass
from Zope.App.OFS.Content.File.FileChunk import FileChunk

class Test( unittest.TestCase ):


    def _makeFile(self, *args, **kw):
        """ """
        from Zope.App.OFS.Content.File.File import File

        return File(*args, **kw)
        

    def testEmpty(self):

        file = self._makeFile()

        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), '')


    def testConstructor(self):

        file = self._makeFile('Foobar')
        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), 'Foobar')
    

        file = self._makeFile('Foobar', 'text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(file.getData(), 'Foobar')


        file = self._makeFile(data='Foobar', contentType='text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(file.getData(), 'Foobar')


    def testMutators(self):

        file = self._makeFile()
        
        file.setContentType('text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')

        file.setData('Foobar')
        self.assertEqual(file.getData(), 'Foobar')

        file.edit('Blah', 'text/html')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')


    def testLargeDataInput(self):
        
        file = self._makeFile()

        # Insert as string
        file.setData('Foobar'*60000)
        self.assertEqual(file.getSize(), 6*60000)
        self.assertEqual(file.getData(), 'Foobar'*60000)

        # Insert data as FileChunk
        fc = FileChunk('Foobar'*4000)
        file.setData(fc)
        self.assertEqual(file.getSize(), 6*4000)
        self.assertEqual(file.getData(), 'Foobar'*4000)

        # Insert data from file object
        import cStringIO
        sio = cStringIO.StringIO()
        sio.write('Foobar'*100000)
        sio.seek(0)
        file.setData(sio)
        self.assertEqual(file.getSize(), 6*100000)
        self.assertEqual(file.getData(), 'Foobar'*100000)
        

    def testInterface(self):
        
        from Zope.App.OFS.Content.File.File import File, IFile

        self.failUnless(IFile.isImplementedByInstancesOf(File))
        self.failUnless(verifyClass(IFile, File))        
        


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )

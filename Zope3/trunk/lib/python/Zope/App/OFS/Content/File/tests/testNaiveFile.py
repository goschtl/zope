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

$Id: testNaiveFile.py,v 1.2 2002/06/10 23:28:00 jim Exp $
"""

import unittest
from Interface.Verify import verifyClass

class Test( unittest.TestCase ):


    def _makeNaiveFile(self, *args, **kw):
        """ """
        from Zope.App.OFS.Content.File.NaiveFile import NaiveFile

        return NaiveFile(*args, **kw)
        

    def testEmpty( self ):

        file = self._makeNaiveFile()

        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), '')


    def testConstructor(self):

        file = self._makeNaiveFile('Foobar')
        self.assertEqual(file.getContentType(), '')
        self.assertEqual(file.getData(), 'Foobar')
    

        file = self._makeNaiveFile('Foobar', 'text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(file.getData(), 'Foobar')


        file = self._makeNaiveFile(data='Foobar', contentType='text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(file.getData(), 'Foobar')


    def testMutators(self):

        file = self._makeNaiveFile()
        
        file.setContentType('text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')

        file.setData('Foobar')
        self.assertEqual(file.getData(), 'Foobar')

        file.edit('Blah', 'text/html')
        self.assertEqual(file.getContentType(), 'text/html')
        self.assertEqual(file.getData(), 'Blah')


    def testInterface(self):
        
        from Zope.App.OFS.Content.File.NaiveFile import NaiveFile
        from Zope.App.OFS.Content.File.IFile import IFile

        self.failUnless(IFile.isImplementedByInstancesOf(NaiveFile))
        self.failUnless(verifyClass(IFile, NaiveFile))        
        


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )

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
import unittest

from Zope.App.OFS.Content.Folder.LoadedFolder import LoadedFolder
from Zope.App.OFS.Content.Folder.FolderLimit import FolderLimitExceededError

class Object:
    """Object stub"""


class Test( unittest.TestCase ):
    

    def testSetLimit( self ):
        """ """
        loadedfolder = LoadedFolder()
        
        loadedfolder.setLimit(5) 
        self.assertEquals( loadedfolder._limit, 5 )


    def testGetLimit( self ):
        """ """
        loadedfolder = LoadedFolder()
        
        loadedfolder._limit = 5 
        self.assertEquals( loadedfolder.getLimit(), 5 )


    def testLimitReach(self):
        """ """
        loadedfolder = LoadedFolder()
        loadedfolder.setObject('object1', Object())
        loadedfolder._limit = 2 

        # A second one should fit in
        loadedfolder.setObject('object2', Object())
        
        # But with 3 go on strike
        self.assertRaises( FolderLimitExceededError,
                           loadedfolder.setObject,
                           'object3', Object() )
         
                
    

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.main()

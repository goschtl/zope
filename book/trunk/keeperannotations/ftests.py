##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Functional tests for KeeperAnnotations

$Id$
"""
import time
import unittest

from zope.app.file import File
from zope.app.tests.functional import BrowserTestCase

from book.keeperannotations import keeper_key

class KeeperFile(File):
    pass

  
class Test(BrowserTestCase):
    """Funcional tests for Keeper Annotations.

    This needs to have the configuration in 'keeper.zcml'
    included in the setup of the functional tests.

    Add the following directive to 'ftesting.zcml':

       <include file="src/book/keeperannotations/keeper.zcml" />

    """

    def test_DC_Annotations(self):
        # Create file
        response = self.publish(
            "/+/action.html?type_name=book.keeperannotations.KeeperFile",
            basic='mgr:mgrpw')
  
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')

        # Update the file's title
        self.publish("/@@contents.html",
                     basic='mgr:mgrpw', 
                     form={'retitle_id' : 'KeeperFile',
                           'new_value' : u'File Title'})
  
        root = self.getRootFolder()
        file = root['KeeperFile']
        ann = root.__annotations__[keeper_key][file]
        dc_ann = ann['zope.app.dublincore.ZopeDublinCore']
        self.assert_(dc_ann[u'Date.Created'][0] > u'2004-01-01T12:00:00')
        self.assert_(dc_ann[u'Date.Created'][0] == dc_ann[u'Date.Modified'][0])
        self.assertEqual(dc_ann[u'Title'][0], u'File Title')
  
  
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))
  
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
      

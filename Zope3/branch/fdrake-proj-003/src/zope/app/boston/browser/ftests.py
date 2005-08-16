##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Boston skin ftests

$Id$
"""

import unittest
from xml.dom import minidom
from zope.app.testing.functional import BrowserTestCase

class TestBostonSkin(BrowserTestCase):


    def test_addFolder(self):
        response = self.publish("/++skin++Boston/+/action.html", 
                                basic='mgr:mgrpw', 
                                form={'type_name':u'zope.app.content.Folder', 
                                      'id':u'folder'})
        self.assertEqual(response.getStatus(), 302)

        response = self.publish("/++skin++Boston/folder/+/action.html", 
                                basic='mgr:mgrpw', 
                                form={'type_name':u'zope.app.content.Folder', 
                                      'id':u'subfolder'})
        self.assertEqual(response.getStatus(), 302)

    def test_addSiteManager(self):
        response = self.publish("/++skin++Boston/+/action.html", 
                                basic='mgr:mgrpw', 
                                form={'type_name':u'zope.app.content.Folder', 
                                      'id':u'folder'})
        self.assertEqual(response.getStatus(), 302)

        response = self.publish("/++skin++Boston/folder/+/action.html", 
                                basic='mgr:mgrpw', 
                                form={'type_name':u'zope.app.content.Folder', 
                                      'id':u'subsite'})
        self.assertEqual(response.getStatus(), 302)

        response = self.publish(
            "/++skin++Boston/folder/subsite/addSiteManager.html", 
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 302)

    def test_css_pagelets(self):
        response = self.publish('/++skin++Boston/', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find('@import url(http://localhost/++skin++Boston/@@/skin.css)') != -1)
        self.assert_(response.getBody().find('@import url(http://localhost/++skin++Boston/@@/widget.css)') != -1)

    def test_javascrip_pagelets(self):
        response = self.publish('/++skin++Boston/', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find('src="http://localhost/++skin++Boston/@@/toggle.js') != -1)

    def test_left_boxes(self):
        # Add a folder
        response = self.publish("/++skin++Boston/+/action.html",
                                basic='mgr:mgrpw', 
                                form={'type_name':u'zope.app.content.Folder', 
                                      'id':u'folder'})
        self.assertEqual(response.getStatus(), 302)
        
        response = self.publish('/++skin++Boston/', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

        # test zmitree cookie box
        self.assert_(response.getBody().find('id="zmicookietreebox"') != -1)

        # test add box
        self.assert_(response.getBody().find('id="addbox"') != -1)

        # test tooltip box. Ah I found one in the role permission view
        response = self.publish('/++skin++Boston/++etc++site/@@AllRolePermissions.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find('id="tooltipbox"') != -1)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBostonSkin))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')


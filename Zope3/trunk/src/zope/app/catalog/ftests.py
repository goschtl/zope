##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Functional tests for catalog

$Id$
"""
import unittest

from zope.app.tests.functional import BrowserTestCase

class TestCatalogAdd(BrowserTestCase):

    def testAddCatalog(self):
        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'zope.app.catalog', 
                                      'id':u'felix_the'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                                         'http://localhost/@@contents.html')

        response = self.publish('/')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find('felix_the') != -1)
        response = self.publish('/felix_the/@@index.html', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find('Advanced Catalog Thingies') != -1)

        # first test the multi-page add screens work
        response = self.publish("/felix_the/+/action.html", 
                        basic='mgr:mgrpw', 
                        form={'type_name':u'AddFieldIndexToCatalog',
                              'id':u'dctitle',})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                 'http://localhost/felix_the/+/AddFieldIndexToCatalog=dctitle')
        response = self.publish("/felix_the/+/AddFieldIndexToCatalog=dctitle",
                        basic='mgr:mgrpw', 
                        form={'field.interface': 
                              u'zope.app.dublincore.interfaces.IZopeDublinCore',
                              'field.field_name':u'Title', 
                              'UPDATE_SUBMIT': u'Submit'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                 'http://localhost/felix_the/@@contents.html')

        # and a couple more indexes now - first a full text index
        response = self.publish("/felix_the/+/AddTextIndexToCatalog=fulltext",
                        basic='mgr:mgrpw', 
                        form={'field.interface':
                               'zope.app.index.interfaces.text.ISearchableText',
                              'field.field_name':'getSearchableText',
                              'UPDATE_SUBMIT': u'Submit'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                 'http://localhost/felix_the/@@contents.html')

        # Single page submit
        response = self.publish("/felix_the/+/AddFieldIndexToCatalog=name",
                        basic='mgr:mgrpw', 
                        form={'field.interface.search': '',
                              'field.field_name':'id',
                               'UPDATE_SUBMIT': u'Submit'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                 'http://localhost/felix_the/@@contents.html')

        # keyword index 
        response = self.publish("/felix_the/+/AddKeywordIndexToCatalog=dccreator",
                        basic='mgr:mgrpw', 
                        form={'field.interface': 
                              u'zope.app.dublincore.interfaces.IZopeDublinCore',
                              'field.field_name':u'Creator', 
                              'UPDATE_SUBMIT': u'Submit'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                 'http://localhost/felix_the/@@contents.html')

        # Check the indexes are there and visible
        response = self.publish('/felix_the/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find('dctitle') != -1)
        self.assert_(response.getBody().find('dccreator') != -1)
        self.assert_(response.getBody().find('fulltext') != -1)
        self.assert_(response.getBody().find('name') != -1)

        # Now add some content
        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'zope.app.content.File', 
                                      'id':u'First'})
        self.assertEqual(response.getStatus(), 302)
        response = self.publish("/First/@@EditMetaData.html",basic='mgr:mgrpw',
                                form={'dctitle':u'First File',
                                      'dcdescription':u'a file with stuff',
                                      'save':u'Save Changes',
                                      })
        self.assertEqual(response.getStatus(), 200)
        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'zope.app.content.File', 
                                      'id':u'Second'})
        self.assertEqual(response.getStatus(), 302)
        response = self.publish("/Second/@@EditMetaData.html",basic='mgr:mgrpw',
                                form={'dctitle':u'Second File',
                                      'dcdescription':u'another file of stuff',
                                      'save':u'Save Changes',
                                      })
        self.assertEqual(response.getStatus(), 200)

        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'zope.app.content.File', 
                                      'id':u'Third'})
        self.assertEqual(response.getStatus(), 302)
        response = self.publish("/Third/@@EditMetaData.html",basic='mgr:mgrpw',
                                form={'dctitle':u'Third File',
                                      'dcdescription':u'something else',
                                      'save':u'Save Changes',
                                      })
        self.assertEqual(response.getStatus(), 200)
        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'zope.app.content.File', 
                                      'id':u'Thirda'})
        self.assertEqual(response.getStatus(), 302)
        response = self.publish("/Thirda/@@EditMetaData.html",basic='mgr:mgrpw',
                                form={'dctitle':u'Third File',
                                      'dcdescription':u'something else',
                                      'save':u'Save Changes',
                                      })
        self.assertEqual(response.getStatus(), 200)
        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'ZPTPage', 
                                      'id':u'Page1'})
        self.assertEqual(response.getStatus(), 302)
        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'ZPTPage', 
                                      'id':u'Page2'})
        self.assertEqual(response.getStatus(), 302)
        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'ZPTPage', 
                                      'id':u'Page3'})
        self.assertEqual(response.getStatus(), 302)

        response = self.publish("/Page1/@@edit.html", basic='mgr:mgrpw', 
                                form={'field.source':u'Some sample text',
                                      'field.expand':u'',
                                      'field.expand.used':u'',
                                      'UPDATE_SUBMIT':u'Submit'})
        self.assertEqual(response.getStatus(), 200)
        response = self.publish("/Page2/@@edit.html", basic='mgr:mgrpw', 
                                form={'field.source':u'Some other text',
                                      'field.expand':u'',
                                      'field.expand.used':u'',
                                      'UPDATE_SUBMIT':u'Submit'})
        self.assertEqual(response.getStatus(), 200)
        response = self.publish("/Page3/@@edit.html", basic='mgr:mgrpw', 
                                form={'field.source':u'Different sample text',
                                      'field.expand':u'',
                                      'field.expand.used':u'',
                                      'UPDATE_SUBMIT':u'Submit'})
        self.assertEqual(response.getStatus(), 200)
        response = self.publish("/Page3/@@EditMetaData.html",basic='mgr:mgrpw',
                                form={'dctitle':u'Third File',
                                      'dcdescription':u'something else',
                                      'save':u'Save Changes',
                                      })
        self.assertEqual(response.getStatus(), 200)

        root = self.getRootFolder()
        cat = root['felix_the']
        name = cat['dctitle']
        self.assertEquals(name.documentCount(), 8)
        res = cat.searchResults(dctitle='Second File')
        self.assertEquals(len(res), 1)
        res = cat.searchResults(dctitle='Third File')
        self.assertEquals(len(res), 3)
        res = cat.searchResults(fulltext='sample')
        self.assertEquals(len(res), 2)
        res = cat.searchResults(fulltext='sample', dctitle='Third File')
        self.assertEquals(len(res), 1)
        res = cat.searchResults(fulltext='fnargle', dctitle='Third File')
        self.assertEquals(len(res), 0)
        res = cat.searchResults(fulltext='sample', dctitle='Zeroth File')
        self.assertEquals(len(res), 0)
        res = cat.searchResults(dccreator='zope.mgr', dctitle='Third File')
        self.assertEquals(len(res), 3)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCatalogAdd))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')


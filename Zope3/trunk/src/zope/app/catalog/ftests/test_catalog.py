import unittest

from zope.testing.functional import BrowserTestCase

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
                        form={'field.interface.search': 
                              u'zope.app.interfaces.dublincore.IZopeDublinCore',
                              'field.field_name':'Title', 
                              'UPDATE_SUBMIT': u'Submit'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                 'http://localhost/felix_the/@@contents.html')

        # and a couple more indexes now
        response = self.publish("/felix_the/+/AddFieldIndexToCatalog=dccreator",
                        basic='mgr:mgrpw', 
                        form={'field.interface.search': 
                              u'zope.app.interfaces.dublincore.IZopeDublinCore',
                              'field.field_name':'Creator',
                               'UPDATE_SUBMIT': u'Submit'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                 'http://localhost/felix_the/@@contents.html')
        response = self.publish("/felix_the/+/AddFieldIndexToCatalog=name",
                        basic='mgr:mgrpw', 
                        form={'field.interface.search': '',
                              'field.field_name':'name',
                               'UPDATE_SUBMIT': u'Submit'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                 'http://localhost/felix_the/@@contents.html')

        # Check the indexes are there and visible
        response = self.publish('/felix_the/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find('dccreator') != -1)
        self.assert_(response.getBody().find('dctitle') != -1)
        
        # Now add some content
        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'File', 
                                      'id':u'First'})
        self.assertEqual(response.getStatus(), 302)
        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'File', 
                                      'id':u'Second'})
        self.assertEqual(response.getStatus(), 302)
        response = self.publish("/+/action.html", basic='mgr:mgrpw', 
                                form={'type_name':u'File', 
                                      'id':u'Third'})
        self.assertEqual(response.getStatus(), 302)

        # Now comes the fun. Functional tests haven't connected up
        # the bloody event service, so we can't do anything useful 
        # yet. *sigh*
        #root = self.getRootFolder()
        #cat = root['felix_the']
        #print cat.searchResults(dctitle='Third')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCatalogAdd))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')


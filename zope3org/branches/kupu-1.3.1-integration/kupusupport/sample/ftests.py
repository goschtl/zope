import unittest
from kupusupport.sample.app import KupuSample
from zope.app.tests import ztapi
from zope.app.tests.functional import BrowserTestCase

class Test(BrowserTestCase):

    def setUp(self):
        BrowserTestCase.setUp(self)
        self.kuputest = KupuSample()
        self.getRootFolder()['kuputest'] = self.kuputest
        self.commit()

    def test_edit(self):
        response = self.publish('/kuputest/@@edit.html', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        for name in ('title', 'description', 'body'):
            self.assert_(getattr(self.kuputest, name) in body)
        #self.assert_('Edit' in body)

    def test_kupueditor(self):
        response = self.publish('/kuputest/@@kupueditor.html', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

    def test_kupucontent(self):
        response = self.publish('/kuputest/@@kupucontent.html', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

    def test_imagelibrary(self):
        response = self.publish('/kuputest/@@imagelibrary.xml', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

    def test_imagelibraries(self):
        response = self.publish('/kuputest/@@imagelibraries.xml', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

def test_suite():
    return unittest.makeSuite(Test)

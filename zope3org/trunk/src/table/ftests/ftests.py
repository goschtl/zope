import unittest
from zope.app.testing.functional import BrowserTestCase
from zope.app.rdb.interfaces import IZopeDatabaseAdapter
from zope.app import zapi
basic = 'mgr:mgrpw'

class RootTestCase(BrowserTestCase):
    
    """ """
    
    def setUp(self):
        super(RootTestCase,self).setUp()
        
    def test_1(self):
        
        url ="/"
        form = {
            'type_name':u'BrowserAdd__zpis.root.PISZRoot',
            'new_value':u'root'
            }
        response = self.publish(url,basic=basic,form=form)
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')
        root = self.getRootFolder()['root']
        response = self.publish('/root/@@edit.html',basic=basic)
        self.assertEqual(response.getStatus(), 200)
        acts1 = root.employees[u'hom'].activities
        self.assertEqual(acts1.__parent__,root.employees[u'hom'])
        acts2 = root.employees[u'fw'].activities
        self.assertEqual(acts2.__parent__,root.employees[u'fw'])
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(RootTestCase),
        ))


if __name__== "__main__":
    unittest.main(defaultTest='test_suite')




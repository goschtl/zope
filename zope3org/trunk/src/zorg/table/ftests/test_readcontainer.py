import unittest
from zope.app.testing.functional import BrowserTestCase
from zope.app.rdb.interfaces import IZopeDatabaseAdapter
from zope.app import zapi
from zope.configuration import xmlconfig
from zope.app.testing import ztapi
import zope
import table
basic = 'mgr:mgrpw'

class RootTestCase(BrowserTestCase):
    
    """ """
    
    def setUp(self):
        super(RootTestCase,self).setUp()


        xmlconfig.string("""
        <configure xmlns:zope="http://namespaces.zope.org/zope"
        xmlns="http://namespaces.zope.org/browser"
        xmlns:i18n="http://namespaces.zope.org/i18n"
        i18n_domain="zope"
        package="table.ftests"
        >
        <include package="zope.app.publisher.browser"
        file="meta.zcml"/>

        <page
        class="table.ftests.testing.TestView"
        for="zope.app.container.interfaces.IReadContainer"
        name="table.html"
        template="test.pt"
        permission="zope.View"/>
        </configure>
        """)
        
    def test_1(self):
        
        url ="/@@table.html"
        response = self.publish(url,basic=basic)
        self.assertEqual(response.getStatus(), 200)
#         self.assertEqual(response.getHeader('Location'),
#                          'http://localhost/@@contents.html')
#         root = self.getRootFolder()['root']
#         response = self.publish('/root/@@edit.html',basic=basic)
#         self.assertEqual(response.getStatus(), 200)
#         acts1 = root.employees[u'hom'].activities
#         self.assertEqual(acts1.__parent__,root.employees[u'hom'])
#         acts2 = root.employees[u'fw'].activities
#         self.assertEqual(acts2.__parent__,root.employees[u'fw'])
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(RootTestCase),
        ))


if __name__== "__main__":
    unittest.main(defaultTest='test_suite')




import unittest

from zope.app.tests import ztapi
from zope.app.tests.functional import BrowserTestCase
from zope.app.generations.generations import SchemaManager, generations_key
from zope.app.generations.interfaces import ISchemaManager

class TestDatabaseSchema(BrowserTestCase):

    def test(self):
        BrowserTestCase.setUp(self)
        
        root = self.getRootFolder()._p_jar.root()
        appkey = 'zope.app.generations.demo'
        root[generations_key][appkey] = 0
        self.commit()
        manager = SchemaManager(0, 3, 'zope.app.generations.demo')

        ztapi.provideUtility(ISchemaManager, manager, appkey)

        response = self.publish('/++etc++process/@@generations.html',
                                basic='mgr:mgrpw')
        body = response.getBody()
        body = ' '.join(body.split())
        expect = ('<td>zope.app.generations.demo</td> '
                  '<td>0</td> <td>3</td> <td>0</td> '
                  '<td> <input type="submit" value=" evolve " '
                  'name="evolve-app-zope.app.generations.demo"> </td>')
        self.assert_(body.find(expect) > 0)

        response = self.publish('/++etc++process/@@generations.html'
                                '?evolve-app-zope.app.generations.demo=evolve',
                                basic='mgr:mgrpw')
        body = response.getBody()
        body = ' '.join(body.split())
        expect = ('<td>zope.app.generations.demo</td> '
                  '<td>0</td> <td>3</td> <td>1</td> '
                  '<td> <input type="submit" value=" evolve " '
                  'name="evolve-app-zope.app.generations.demo"> </td>')
        self.assert_(body.find(expect) > 0)

        response = self.publish('/++etc++process/@@generations.html'
                                '?evolve-app-zope.app.generations.demo=evolve',
                                basic='mgr:mgrpw')
        body = response.getBody()
        body = ' '.join(body.split())
        expect = ('<td>zope.app.generations.demo</td> '
                  '<td>0</td> <td>3</td> <td>2</td> '
                  '<td> <input type="submit" value=" evolve " '
                  'name="evolve-app-zope.app.generations.demo"> </td>')
        self.assert_(body.find(expect) > 0)

        response = self.publish('/++etc++process/@@generations.html'
                                '?evolve-app-zope.app.generations.demo=evolve',
                                basic='mgr:mgrpw')
        body = response.getBody()
        body = ' '.join(body.split())
        expect = ('<td>zope.app.generations.demo</td> '
                  '<td>0</td> <td>3</td> <td>3</td> '
                  '<td> <span>')
        self.assert_(body.find(expect) > 0)

        ztapi.unprovideUtility(ISchemaManager, appkey)

        
def test_suite():
    return unittest.makeSuite(TestDatabaseSchema)

import unittest
from buddydemo.buddy import Buddy
from zope.app.testing.functional import BrowserTestCase

class Test(BrowserTestCase):

    def setUp(self):
        BrowserTestCase.setUp(self)
        self.bob = Buddy('Bob', 'Smith', 'bob@smith.org',
                    '513 Princess Ann Street', '22401')
        self.getRootFolder()['bob'] = self.bob
        self.commit()
    
    def test_buddy_display(self):
        response = self.publish('/bob')
        body = response.getBody()
        for name in ('first', 'last', 'email',
                     'address', 'postal_code'):
            self.assert_(getattr(self.bob, name) in body)
        self.assert_('Fredericksburg' in body)
        self.assert_('Virginia' in body)

    def test_buddy_edit(self):
        response = self.publish('/bob/edit.html', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

    def test_buddy_add(self):
        response = self.publish('/+/AddBuddy.html', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        
def test_suite():
    return unittest.makeSuite(Test)

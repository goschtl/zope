import unittest
from Products.CMFCore.ActionsTool import *
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression

class ActionInformationTests(unittest.TestCase):
    
    def test_basic_construction(self):
        ai = ActionInformation(id='view'
                              )
        self.assertEqual(ai.getId(), 'view')
        self.assertEqual(ai.Title(), 'view')
        self.assertEqual(ai.Description(), '')
        self.assertEqual(ai.getCondition(), '')
        self.assertEqual(ai.getActionExpression(), '')
        self.assertEqual(ai.getPermissions(), ())

    def test_construction_with_Expressions(self):
        ai = ActionInformation(id='view'
                             , title='View'
                             , action=Expression(
             text='view')
                             , condition=Expression(
             text='member'))
        self.assertEqual(ai.getId(), 'view')
        self.assertEqual(ai.Title(), 'View')
        self.assertEqual(ai.Description(), '')
        self.assertEqual(ai.getCondition(), 'member')
        self.assertEqual(ai.getActionExpression(), 'view')
        self.assertEqual(ai.getPermissions(), ())
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ActionInformationTests))
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()

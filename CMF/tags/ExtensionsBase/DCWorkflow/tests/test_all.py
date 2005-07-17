import Zope
import unittest
#from Products.DCWorkflow.tests import test_DCWorkflow

def test_suite():
    suite = unittest.TestSuite()
    #suite.addTest( test_DCWorkflow.test_suite() )
    return suite

def run():
    if hasattr( unittest, 'JUnitTextTestRunner' ):
        unittest.JUnitTextTestRunner().run( test_suite() )
    else:
        unittest.TextTestRunner( verbosity=0 ).run( test_suite() )

if __name__ == '__main__':
    run()

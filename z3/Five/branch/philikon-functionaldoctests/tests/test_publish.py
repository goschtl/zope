import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
from Testing.ZopeTestCase.functional import FunctionalDocFileSuite

# we need to install FiveTest *before* Five as Five
# looks up zcml files in the products it can find.
ZopeTestCase.installProduct('FiveTest')
ZopeTestCase.installProduct('Five')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(FunctionalDocFileSuite('publish.txt',
                                         package="Products.Five.tests"))
    return suite

if __name__ == '__main__':
    framework()

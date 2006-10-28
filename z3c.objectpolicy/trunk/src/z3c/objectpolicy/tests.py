import unittest
from zope import component
from zope.app.testing import placelesssetup
from zope.configuration import xmlconfig
from zope.testing import module
from zope.app.securitypolicy.tests.test_zopepolicy import setUp

from z3c.objectpolicy.objectpolicy import ObjectPrincipalPermissionManager
from z3c.objectpolicy.objectpolicy import ObjectRolePermissionManager

def setUpOP(test):
    setUp(test)

    component.provideAdapter(ObjectPrincipalPermissionManager)
    component.provideAdapter(ObjectRolePermissionManager)

def tearDown(test):
    placelesssetup.tearDown()

def test_suite():
    from zope.testing import doctest
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'lowlevel.txt',
            setUp=setUp, tearDown=tearDown,
            ),
        doctest.DocFileSuite(
            'highlevel.txt',
            setUp=setUp, tearDown=tearDown,
            ),
        doctest.DocFileSuite(
            'zopepolicy_copy.txt',
            setUp=setUpOP, tearDown=tearDown,
            ),
        doctest.DocFileSuite(
            'zopepolicy_objectpolicy.txt',
            setUp=setUpOP, tearDown=tearDown,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

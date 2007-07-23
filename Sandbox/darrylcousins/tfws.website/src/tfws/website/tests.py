import unittest
from zope.testing import doctest
from zope.app.testing import setup, ztapi

from zope.annotation.interfaces import IAnnotatable
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.securitypolicy.principalrole \
     import AnnotationPrincipalRoleManager

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def setUp(test):
    root = setup.placefulSetUp(site=True)
    test.globs['root'] = root
    ztapi.provideAdapter(IAnnotatable, IPrincipalRoleManager,
                            AnnotationPrincipalRoleManager)

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('site.txt',
                       setUp=setUp, tearDown=tearDown,
                       optionflags=optionflags),
                   ])

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


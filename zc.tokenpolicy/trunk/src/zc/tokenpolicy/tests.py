import unittest
from zope.app.testing import placelesssetup
from zope.configuration import xmlconfig
from zope.testing import module

import zc.sharing.sharing

from zc.tokenpolicy import policy

def zcml(s):
    context = xmlconfig.file('meta.zcml', package=zc.tokenpolicy)
    xmlconfig.string(s, context)

def zcmlSetUp(test):
    placelesssetup.setUp()
    zc.sharing.sharing.definePrivilege(0, u'Read')
    zc.sharing.sharing.definePrivilege(2, u'Write')
    zc.sharing.sharing.definePrivilege(4, u'Share')
    module.setUp(test, 'zc.tokenpolicy.zcml_text')

def zcmlTearDown(test):
    for pid in policy.getPrivileges():
       policy.removePrivilege(pid)
    zc.sharing.sharing.clearPrivileges()
    module.tearDown(test, 'zc.tokenpolicy.zcml_text')
    placelesssetup.tearDown()

def setUp(test):
    placelesssetup.setUp()
    zc.sharing.sharing.definePrivilege(0, u'Read')
    zc.sharing.sharing.definePrivilege(2, u'Write')
    zc.sharing.sharing.definePrivilege(4, u'Share')

def tearDown(test):
    zc.sharing.sharing.clearPrivileges()
    for pid in policy.getPrivileges():
       policy.removePrivilege(pid)
    placelesssetup.tearDown()

def test_suite():
    from zope.testing import doctest
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'zcml.txt', globs={'zcml': zcml},
            setUp=zcmlSetUp, tearDown=zcmlTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE,
            ),
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            ),
#        doctest.DocFileSuite(
#            'index.txt',
#            setUp=placelesssetup.setUp, tearDown=tearDownIndex,
#            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

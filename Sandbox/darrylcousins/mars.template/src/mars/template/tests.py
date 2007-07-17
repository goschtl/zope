import unittest
from zope.testing import doctest

import zope.interface

from martian.interfaces import IModuleInfo

class ModuleInfo(object):
    zope.interface.implements(IModuleInfo)
    path = ''
    package_dotted_name = ''

    def getAnnotation(self, name, default):
        return default

globs = dict(module_info=ModuleInfo())

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def setUp(test):
    pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('./template.txt',
                             setUp=setUp, globs=globs,
                             optionflags=optionflags),
                   ])

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


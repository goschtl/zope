import unittest
from zope.testing import doctest

import zope.interface
from zope.configuration.config import ConfigurationMachine

from martian.interfaces import IModuleInfo

class ModuleInfo(object):
    zope.interface.implements(IModuleInfo)
    path = ''
    package_dotted_name = ''

    def getAnnotation(self, name, default):
        return default

globs = dict(module_info=ModuleInfo(),
             config=ConfigurationMachine())

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('./template.txt',
                             globs=globs,
                             optionflags=optionflags),
                   ])

    return suite

import unittest

import zope.interface
from zope.testing import doctest
from zope.app.testing import setup
from zope.configuration.config import ConfigurationMachine

from martian.interfaces import IModuleInfo

class ModuleInfo(object):
    zope.interface.implements(IModuleInfo)
    path = ''
    package_dotted_name = ''

    def getAnnotation(self, name, default):
        return default

globs = dict(module_info=ModuleInfo(),
             config=ConfigurationMachine(),
             root=setup.placefulSetUp(True))

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def setUp(test):
    

    import zope.component
    import zope.traversing
    zope.component.provideAdapter(
        zope.traversing.adapters.DefaultTraversable,
        [None],
        )

    # register provider TALES
    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('view.txt',
                             setUp=setUp, globs=globs,
                             optionflags=optionflags),
                   ])

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')




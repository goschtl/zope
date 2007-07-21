import unittest
from zope.testing import doctest
from zope.app.testing import setup
import zope.interface

from martian.interfaces import IModuleInfo

class ModuleInfo(object):
    zope.interface.implements(IModuleInfo)
    path = ''
    package_dotted_name = ''

    def getAnnotation(self, name, default):
        return default

from zope.app.testing import setup
globs = dict(module_info=ModuleInfo(), root=setup.placefulSetUp(True))

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def setUp(test):
    from z3c.form import testing
    testing.setupFormDefaults()
    # register provider TALES
    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

def widgetSetUp(test):
    setup.placefulSetUp(True)

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('./form.txt',
                             setUp=setUp, globs=globs, tearDown=tearDown,
                             optionflags=optionflags),
                    doctest.DocFileSuite('./widget.txt',
                             setUp=widgetSetUp, globs=globs, tearDown=tearDown,
                             optionflags=optionflags),
                   ])

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


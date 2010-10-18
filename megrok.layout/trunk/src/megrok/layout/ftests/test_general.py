import unittest
import doctest
from zope.testing import cleanup
from zope.testing import module
import zope.component.eventtesting
from zope import component
from megrok import layout
from grokcore.component.testing import grok_component as default_grok_component


def grok_component(name, component, **kwargs):
    # Because of undocumented but ok change in grokcore.component,
    # grok_component doesn't work anymore in doctests.
    component.__grok_module__ = 'megrok.layout'
    return default_grok_component(name, component, **kwargs)


def moduleSetUp(test):
    module.setUp(test, '__main__')

def moduleTearDown(test):
    module.tearDown(test)
    cleanup.cleanUp()

def zopeSetUp(test):
    zope.component.eventtesting.setUp(test)

def zopeTearDown(test):
    cleanup.cleanUp()

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {'grok_component': grok_component}
    suite = unittest.TestSuite()

    suite.addTest(
        doctest.DocFileSuite(
            '../README.txt',
            optionflags=optionflags,
            setUp=moduleSetUp,
            tearDown=moduleTearDown,
            globs=globs)
        )

    return suite

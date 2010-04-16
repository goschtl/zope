"""Monkeypatches of stdlibs doctest to make it behave more like 
zope.testing.doctest, so we can test zope.testing properly with doctest.
"""
import imp
import sys
import unittest

def normalize_module_path(module_path):
    if module_path.endswith('.pyc'):
        module_path = module_path[:-1]
    return module_path

def absolute_import(name):
    """Imports a module with an absolute name, when there is a relative name clash

    Gotten from Benji York's "Manuel" module.
    """
    module_path = normalize_module_path(imp.find_module(name)[1])

    # don't create a new module object if there's already one that we can reuse
    for module in sys.modules.values():
        if module is None or not hasattr(module, '__file__'):
            continue
        if module_path == normalize_module_path(module.__file__):
            return module

    return imp.load_module(name, *imp.find_module(name))

doctest = absolute_import('doctest')


def new_init(self, test, optionflags=0, setUp=None, tearDown=None,
             checker=None):
    unittest.TestCase.__init__(self)
    self._dt_optionflags = optionflags
    self._dt_checker = checker
    self._dt_test = test
    self._dt_setUp = setUp
    self._dt_tearDown = tearDown
    self._dt_globs = test.globs.copy()

def new_tearDown(self):
    test = self._dt_test

    if self._dt_tearDown is not None:
        self._dt_tearDown(test)

    test.globs.clear()
    test.globs.update(self._dt_globs)

doctest.DocTestCase.__init__ = new_init
doctest.DocTestCase.tearDown = new_tearDown

if sys.version_info < (3,):
    from StringIO import StringIO
    
    def new_write(self, value):
        if isinstance(value, unicode):
            value = value.encode('utf8')
        StringIO.write(self, value)
    
    doctest._SpoofOut.write = new_write

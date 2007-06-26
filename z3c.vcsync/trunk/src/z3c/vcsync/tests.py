import unittest
from zope.testing import doctest, cleanup
import tempfile
import shutil
import py.path
from datetime import datetime
import grok

from zope.interface import implements, Interface
from zope.app.container.interfaces import IContainer
from zope.exceptions.interfaces import DuplicationError

from z3c.vcsync.interfaces import ISerializer, IVcDump, IVcLoad, IVcFactory, IModified
from z3c.vcsync import vc

class TestCheckout(vc.CheckoutBase):
    def __init__(self, path):
        super(TestCheckout, self).__init__(path)
        self.update_function = None

    def up(self):
        # call update_function which will modify the checkout as might
        # happen in a version control update. Function should be set before
        # calling this in testing code
        self.update_function()

    def resolve(self):
        pass

    def commit(self, message):
        pass

class Container(object):
    implements(IContainer)
    
    def __init__(self):
        self.__name__ = None
        self._data = {}

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def __contains__(self, name):
        return name in self.keys()
    
    def __setitem__(self, name, value):
        if name in self._data:
            raise DuplicationError
        self._data[name] = value
        value.__name__ = name
        
    def __getitem__(self, name):
        return self._data[name]

    def __delitem__(self, name):
        del self._data[name]

def setUpZope(test):
    pass

def cleanUpZope(test):
    for dirpath in _test_dirs:
        shutil.rmtree(dirpath)
    cleanup.cleanUp()

_test_dirs = []

def create_test_dir():
    dirpath = tempfile.mkdtemp()
    _test_dirs.append(dirpath)
    return py.path.local(dirpath)

def rel_paths(checkout, paths):
    result = []
    start = len(checkout.path.strpath)
    for path in paths:
        result.append(path.strpath[start:])
    return sorted(result)


globs = {'Container': Container,
         'TestCheckout': TestCheckout,
         'create_test_dir': create_test_dir,
         'rel_paths': rel_paths}

def test_suite():
    suite = unittest.TestSuite([
        doctest.DocFileSuite(
        'README.txt',
        setUp=setUpZope,
        tearDown=cleanUpZope,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

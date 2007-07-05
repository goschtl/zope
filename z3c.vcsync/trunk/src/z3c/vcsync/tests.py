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

from z3c.vcsync.interfaces import (ISerializer, IVcDump, IVcFactory,
                                   IState, ICheckout)
from z3c.vcsync import vc

class TestCheckout(object):
    grok.implements(ICheckout)
    
    def __init__(self, path):
        self.path = path
        self.update_function = None
        self._files = []
        self._removed = []
        
    def up(self):
        # call update_function which will modify the checkout as might
        # happen in a version control update. Function should be set before
        # calling this in testing code
        self.update_function()

    def resolve(self):
        pass

    def commit(self, message):
        pass

    def files(self, dt):
        return self._files

    def removed(self, dt):
        return self._removed
    
class TestState(object):
    grok.implements(IState)

    def __init__(self, root):
        self.root = root
        self.removed_paths = []

    def objects(self, dt):
        for container in self.containers(dt):
            for item in container.values():
                if not IContainer.providedBy(item):
                    yield item
            # yield container after items in container,
            # to test creation of directories when items are
            # thrown up that don't have directories yet
            yield container

    def removed(self, dt):
        return self.removed_paths
    
    def containers(self, dt):
        return self._containers_helper(self.root)

    def _containers_helper(self, container):
        yield container
        for obj in container.values():
            if not IContainer.providedBy(obj):
                continue
            for sub_container in self._containers_helper(obj):
                yield sub_container

class Container(object):
    implements(IContainer)
    
    def __init__(self):
        self.__name__ = None
        self.__parent__ = None
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
        value.__parent__ = self
        
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
         'TestState': TestState,
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

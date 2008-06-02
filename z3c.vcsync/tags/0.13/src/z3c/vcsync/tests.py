import unittest
from zope.testing import doctest, cleanup
import tempfile
import shutil
import py.path
from py.__.path.svn import svncommon
from datetime import datetime
import grok
from zope import component

from zope.interface import implements, Interface
from zope.app.container.interfaces import IContainer
from zope.exceptions.interfaces import DuplicationError

from z3c.vcsync.interfaces import (ISerializer, IDump, IFactory, IParser,
                                   IState, ICheckout)
from z3c.vcsync import vc

class TestCheckout(object):
    grok.implements(ICheckout)
    
    def __init__(self, path):
        self.path = path
        self.update_function = None
        self._files = []
        self._removed = []
        self._revision_nr = 0
        
    def up(self):
        # call update_function which will modify the checkout as might
        # happen in a version control update. Function should be set before
        # calling this in testing code
        self._revision_nr += 1
        self.update_function()

    def resolve(self):
        pass

    def commit(self, message):
        pass

    def files(self, revision_nr):
        return self._files

    def removed(self, revision_nr):
        return self._removed

    def revision_nr(self):
        return self._revision_nr
 
class TestAllState(vc.AllState):
    
    def __init__(self, root):
        super(TestAllState, self).__init__(root)
        self.removed_paths = []

    def removed(self, revision_nr):
        return self.removed_paths

class Item(object):
    def __init__(self, payload):
        self.payload = payload
    def _get_payload(self):
        return self._payload
    def _set_payload(self, value):
        self._payload = value
        self.revision_nr = self.get_revision_nr()
    payload = property(_get_payload, _set_payload)

class TestState(object):
    implements(IState)
    def __init__(self, root):
        self.root = root
        self._removed = []
    def set_revision_nr(self, nr):
        self.root.nr = nr
    def get_revision_nr(self):
        try:
            return self.root.nr
        except AttributeError:
            return 0
    def removed(self, revision_nr):
        return self._removed
    def objects(self, revision_nr):
        for container in self._containers(revision_nr):
            for value in container.values():
                if isinstance(value, Container):
                    continue
                if value.revision_nr >= revision_nr:
                    yield value
    def _containers(self, revision_nr):
        return self._containers_helper(self.root)
    def _containers_helper(self, container):
        yield container
        for obj in container.values():
            if not isinstance(obj, Container):
                continue
            for sub_container in self._containers_helper(obj):
                yield sub_container

class ItemSerializer(grok.Adapter):
    grok.provides(ISerializer)
    grok.context(Item)
    def serialize(self, f):
        f.write(str(self.context.payload))
        f.write('\n')
    def name(self):
        return self.context.__name__ + '.test'

class ItemParser(grok.GlobalUtility):
    grok.provides(IParser)
    grok.name('.test')
    def __call__(self, object, path):
        object.payload = int(path.read())

class ItemFactory(grok.GlobalUtility):
  grok.provides(IFactory)
  grok.name('.test')
  def __call__(self, path):
      parser = component.getUtility(IParser, '.test')
      item = Item(None) # dummy payload
      parser(item, path)
      return item

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

    def __repr__(self):
        return "<Container %s>" % (self.__name__)

class ContainerParser(grok.GlobalUtility):
    grok.provides(IParser)
    def __call__(self, object, path):
        pass

class ContainerFactory(grok.GlobalUtility):
    grok.provides(IFactory)
    def __call__(self, path):
        return Container()

def svn_repo_wc():
    """Create an empty SVN repository.

    Based on an internal testing function of the py library.
    """    
    repo = py.test.ensuretemp('testrepo')
    wcdir = py.test.ensuretemp('wc')
    if not repo.listdir():
        repo.ensure(dir=1)
        py.process.cmdexec('svnadmin create "%s"' %
                           svncommon._escape_helper(repo))
        wcdir.ensure(dir=1)
        wc = py.path.svnwc(wcdir)
        if py.std.sys.platform == 'win32':
            repo = '/' + str(repo).replace('\\', '/')
        wc.checkout(url='file://%s' % repo)
    else:
        wc = py.path.svnwc(wcdir)
    return "file://%s" % repo, wc

def setUpZope(test):
    _test_dirs = []

def cleanUpZope(test):
    for dirpath in _test_dirs:
        shutil.rmtree(dirpath, ignore_errors=True)
    cleanup.cleanUp()

_test_dirs = []

def create_test_dir():
    dirpath = tempfile.mkdtemp()
    _test_dirs.append(dirpath)
    return py.path.local(dirpath)

globs = {}

def test_suite():
    suite = unittest.TestSuite([
        doctest.DocFileSuite(
        'internal.txt',
        setUp=setUpZope,
        tearDown=cleanUpZope,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),

        doctest.DocFileSuite(
        'importexport.txt',
        setUp=setUpZope,
        tearDown=cleanUpZope,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),

        doctest.DocFileSuite(
        'README.txt',
        setUp=setUpZope,
        tearDown=cleanUpZope,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),

        doctest.DocFileSuite(
        'conflict.txt',
        setUp=setUpZope,
        tearDown=cleanUpZope,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),

        ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

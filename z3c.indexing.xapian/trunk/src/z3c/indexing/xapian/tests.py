from zope import interface
from zope import component

import zope.component.testing
import zope.testing

import unittest
import shutil

from persistent import Persistent

class Content(Persistent):
    __parent__ = None
  
    @property 
    def __name__(self):
        return self.title
    
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __hash__(self):
        return hash(self.title)

def setUp(test):
    zope.component.testing.setUp(test)
    
def tearDown(test):
    zope.component.testing.tearDown(test)
    test.globs['db'].close()

    try:
        shutil.rmtree('tmp.idx')
    except OSError:
        pass
    
def test_suite():
    globs = dict(interface=interface, component=component, Content=Content)
    
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            globs=globs,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
from Testing.ZopeTestCase.doctest import DocFileSuite

ZopeTestCase.installProduct('Five')

# hack to have doctests behave like a Python module
class FakeModule:
    def __init__(self, dict):
        self.__dict = dict
    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError, name

def setUp(test):
    name = 'Products.Five.tests.recursion'
    test.globs['__name__'] = name    
    sys.modules[name] = FakeModule(test.globs)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocFileSuite('recursion.txt',
                               package='Products.Five.tests',
                               setUp=setUp))
    return suite

if __name__ == '__main__':
    framework()

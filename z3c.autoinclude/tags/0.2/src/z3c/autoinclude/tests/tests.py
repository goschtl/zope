import doctest
import unittest
import os
from zc.buildout import testing
from pprint import pprint

def test_suite():
    projects_dir = os.path.dirname(__file__)
    base_suite = doctest.DocFileSuite('../README.txt',
                                      setUp=testing.buildoutSetUp,
                                      tearDown=testing.buildoutTearDown,
                                      globs=dict(projects_dir=projects_dir,
                                                 pprint=pprint),
                                      optionflags=doctest.ELLIPSIS)
    return unittest.TestSuite((base_suite,
                               ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

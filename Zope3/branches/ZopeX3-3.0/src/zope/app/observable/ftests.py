import unittest
from persistent import Persistent
from zope.interface import implements
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.tests.functional import FunctionalDocFileSuite

class Chicken(Persistent):
     implements(IAttributeAnnotatable)

def test_suite():
    globs = {'Chicken': Chicken}
    return unittest.TestSuite((
	FunctionalDocFileSuite('observable.txt', globs=globs),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

import unittest

from zope.testing import doctest
from zope.app.testing import placelesssetup
from zope import component

from hurry.file.file import IdFileRetrieval
from hurry.file.interfaces import IFileRetrieval

def fileSetUp(doctest):
    placelesssetup.setUp()
    component.provideUtility(IdFileRetrieval(), IFileRetrieval)
    
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=fileSetUp, tearDown=placelesssetup.tearDown,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


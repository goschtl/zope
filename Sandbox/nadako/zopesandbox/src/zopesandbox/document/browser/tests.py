import unittest
from zope.testing import doctest
from zope.app.testing.functional import FunctionalDocFileSuite

from zopesandbox.document.testing import DocumentLayer

def test_suite():
    readme = FunctionalDocFileSuite('README.txt', optionflags=doctest.ELLIPSIS)
    readme.layer = DocumentLayer
    return unittest.TestSuite((
        readme,
    ))

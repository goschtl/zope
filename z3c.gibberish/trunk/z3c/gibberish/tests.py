import unittest, os, tempfile, shutil
from zope.testing import doctest

def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        optionflags=doctest.REPORT_NDIFF|doctest.NORMALIZE_WHITESPACE)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

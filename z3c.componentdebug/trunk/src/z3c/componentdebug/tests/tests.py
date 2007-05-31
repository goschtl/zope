import unittest
from zope.testing import doctest 

def test_suite():
    suite = doctest.DocFileSuite(
        'site.txt',
        '../README.txt',
        'component.txt',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')

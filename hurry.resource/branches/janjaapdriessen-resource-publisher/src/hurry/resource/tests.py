import unittest, doctest

def test_suite():
    readme = doctest.DocFileSuite(
        'README.txt',
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    return unittest.TestSuite([readme])

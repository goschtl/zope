import unittest, doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('hurry.filesize.filesize'),
        ))

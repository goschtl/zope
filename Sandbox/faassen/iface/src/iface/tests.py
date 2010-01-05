import unittest, doctest

def test_suite():
    suite = unittest.TestSuite()

    optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

    suite.addTests([
            doctest.DocFileSuite('mapping.txt',
                                 optionflags=optionflags)])
    return suite


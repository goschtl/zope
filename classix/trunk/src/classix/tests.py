import unittest, doctest

globs = {}
optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite('README.txt',
                             globs=globs,
                             optionflags=optionflags),
        ])
    return suite

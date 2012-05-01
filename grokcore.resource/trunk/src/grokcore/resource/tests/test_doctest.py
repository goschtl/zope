import unittest
import doctest
import grokcore.resource.testing

def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite('../README.txt',
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    readme.layer = grokcore.resource.testing.browser_layer
    suite.addTest(readme)
    return suite

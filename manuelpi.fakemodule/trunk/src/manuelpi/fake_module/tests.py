import manuel.testing
import manuel.doctest
import manuel.ignore
import manuel.capture
import manuelpi.fake_module
import re
import unittest

# Dependency on manuel
from zope.testing import doctest, renormalizing

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    checker = renormalizing.RENormalizing([
        (re.compile(r'<zope\.testing\.doctest\.'), '<doctest.'),
        ])

    tests = ['README.txt', 'fake_module.txt']

    m = manuel.ignore.Manuel()
    m += manuel.doctest.Manuel(optionflags=optionflags, checker=checker)
    m += manuel.capture.Manuel()
    m += manuelpi.fake_module.Manuel()
    return manuel.testing.TestSuite(m, *tests)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())

import unittest
import doctest
from zope.testing.doctestunit import DocTestSuite,DocFileSuite

from ocql.compiler import compiler

def run(expr):
    return eval(compiler.compile(expr))

def setup(test):
    test.__save_relax = compiler.RELAX_COMPILE
    compiler.RELAX_COMPILE = True

    compiler.registerAdapters()

def teardown(test):
    compiler.RELAX_COMPILE = test.__save_relax

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
        DocFileSuite('rewriter.txt',
            optionflags=flags),
        DocFileSuite('algebra.txt',
            optionflags=flags,
            globs={'run': run},
            setUp = setup, tearDown = teardown),
        DocFileSuite('algebra_checks.txt',
            optionflags=flags),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

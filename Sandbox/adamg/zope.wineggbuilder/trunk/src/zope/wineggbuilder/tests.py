"""tests

$Id$
"""
__docformat__ = 'ReStructuredText'

import unittest
import doctest
import pprint

#format is [(expected cmd, result)]
CommandIO = []

class MockCommand(object):
    def __init__(self):
        pass

    def do(cmd):
        global CommandIO
        next = CommandIO.pop(0)
        if next[0] != cmd:
            raise ValueError("Wrong command, expected: %s, got: %s",
                             (next[0], cmd))

        if isinstance(next[1], Exception):
            raise next[1]

        return next[1]


    def __call__(self, cwd=None, captureOutput=True, exitOnError=True):
        return self

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     globs={'pprint': pprint}
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

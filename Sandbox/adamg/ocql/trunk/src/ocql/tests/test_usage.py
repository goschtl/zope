# -*- coding: UTF-8 -*-

"""Main

$Id$
"""

import unittest
import doctest
from zope.testing.doctestunit import DocTestSuite,DocFileSuite

from ocql.engine import OCQLEngine
from ocql.testing.stubs import *

from ocql.testing import utils

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
        DocFileSuite('../USAGE.txt',
                     optionflags=flags),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
# -*- coding: UTF-8 -*-

"""Main

$Id: test_skeleton.py 89812 2008-08-13 18:44:25Z adamg $
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
        DocFileSuite('functions.txt',
                     optionflags=flags,
                     setUp = utils.setupAdapters),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

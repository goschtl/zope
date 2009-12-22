##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Untrusted python tests

$Id$
"""
import unittest
import re
from zope.testing import doctest, renormalizing

def test_suite():
    checker = renormalizing.RENormalizing([
       (re.compile(r"'ImmutableModule' object"),
 	           r'object'),
       ])
    return unittest.TestSuite((
        doctest.DocFileSuite('builtins.txt',
                                 'rcompile.txt',
                                 'interpreter.txt',checker=checker
                                 ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


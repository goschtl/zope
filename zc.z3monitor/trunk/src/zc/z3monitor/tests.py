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
import re, unittest
from zope.testing import doctest, renormalizing

import logging, sys


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            checker=renormalizing.RENormalizing([
                (re.compile("Vm(Size|RSS):\s+\d+\s+kB"), 'Vm\\1 NNN kB'),
                (re.compile("\d\d+\s+\d\d+\s+\d+"), 'RRR WWW C'),
                (re.compile("\d+[.]\d+ seconds"), 'N.NNNNNN seconds'),
                ]),
            ),
        
        ))

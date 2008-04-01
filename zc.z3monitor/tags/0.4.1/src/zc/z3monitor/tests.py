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
import logging, sys

import ZODB.MappingStorage

from zope.testing import doctest, renormalizing


class FauxCache:

    @property
    def fc(self):
        return self

    def getStats(self):
        return 42, 4200, 23, 2300, 1000

def is_connected(self):
    return self._is_connected

ZODB.MappingStorage.MappingStorage._cache = FauxCache()
ZODB.MappingStorage.MappingStorage._is_connected = True
ZODB.MappingStorage.MappingStorage.is_connected = is_connected

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            checker=renormalizing.RENormalizing([
                (re.compile("Vm(Size|RSS):\s+\d+\s+kB"), 'Vm\\1 NNN kB'),
                (re.compile("\d+[.]\d+ seconds"), 'N.NNNNNN seconds'),
                ]),
            ),
        
        ))

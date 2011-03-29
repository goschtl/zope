##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

import doctest
import re
import zope.testing.renormalizing

checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r'/[A-Za-z0-9_/ ]*zc.monitorpdb/src/zc/monitorpdb'),
     r'/zc.monitorpdb/src/zc/monitorpdb'),
    (re.compile(r'^\s*\d+', re.MULTILINE), r'NN'),
    (re.compile(r'.py\(\d+\)', re.MULTILINE), r'.py(NN)'),
    ])


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        checker=checker,
        optionflags=doctest.NORMALIZE_WHITESPACE)

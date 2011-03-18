##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
__docformat__ = "reStructuredText"

import unittest
import zope.testing.doctest
import zope.testing.renormalizing
import re

def test_suite():
    return zope.testing.doctest.DocFileSuite(
        "README.txt",
        "datagram.txt",
        checker=zope.testing.renormalizing.RENormalizing([
            (re.compile(r'0L, '), '0, '),
            (re.compile(r'9L, '), '9, '),
            ]),
        optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE|
                     zope.testing.doctest.ELLIPSIS)

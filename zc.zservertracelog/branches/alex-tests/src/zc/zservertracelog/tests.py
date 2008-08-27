##############################################################################
#
# Copyright (c) 2008 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""tracelog tests
"""
__docformat__ = "reStructuredText"

from zope.testing import doctest
import re
import unittest
import zope.testing.renormalizing


checker = zope.testing.renormalizing.RENormalizing([
    # normalize the channel id and iso8601 timestamp
    (re.compile(r'-?\d+ \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'),
        '23418928 2008-08-26T10:55:00'),
    ])


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileTest(
            'README.txt',
            optionflags=(
                doctest.NORMALIZE_WHITESPACE
                | doctest.ELLIPSIS
                | doctest.INTERPRET_FOOTNOTES),
            checker=checker,
            ),
        ])

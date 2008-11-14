##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
"""
$Id$
"""

import doctest, unittest
from lovely.zetup.testing import PasteAppLayer
from zope.testing.doctest import DocFileSuite

testPasteAppLayer = PasteAppLayer('config:paste.ini')

def test_suite():
    layer = DocFileSuite('layer.txt',
                         optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                         )
    layer.layer = testPasteAppLayer
    return unittest.TestSuite((layer,))

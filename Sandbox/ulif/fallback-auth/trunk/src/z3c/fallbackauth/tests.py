##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

from zope.testing import doctest, cleanup
from zope.app.authentication.placelesssetup import PlacelessSetup

def setUp(test):
    pls = PlacelessSetup().setUp()

def tearDown(test):
    cleanup.cleanUp()

def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp,
        tearDown=tearDown,
        optionflags=doctest.ELLIPSIS+
                    doctest.NORMALIZE_WHITESPACE
        )

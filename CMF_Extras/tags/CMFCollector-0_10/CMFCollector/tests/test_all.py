##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFCollector tests.

$Id$
"""

from unittest import main
import Testing
import Zope2
Zope2.startup()

from Products.CMFCore.tests.base.utils import build_test_suite


def suite():
    return build_test_suite( 'Products.CMFCollector.tests'
                           , [ 'test_CollectorSubset'
                             ,
                             ]
                           )

def test_suite():
    # Just to silence the top-level test.py
    return None

if __name__ == '__main__':
    main(defaultTest='suite')


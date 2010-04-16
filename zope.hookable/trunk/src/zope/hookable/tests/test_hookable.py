##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Test the hookable support Extension

$Id$
"""

import doctest

def test_suite():
    return doctest.DocTestSuite('zope.hookable',
                                optionflags=doctest.ELLIPSIS |
                                            doctest.IGNORE_EXCEPTION_DETAIL,
                               )

if __name__ == '__main__':
    import unittest
    unittest.main()

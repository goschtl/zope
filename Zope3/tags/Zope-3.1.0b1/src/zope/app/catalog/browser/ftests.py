##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional tests for xmlrpc

$Id: ftests.py 27323 2004-08-28 19:31:22Z jim $
"""
from zope.app.testing.functional import FunctionalDocFileSuite

def test_suite():
    return FunctionalDocFileSuite('README.txt')

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite')

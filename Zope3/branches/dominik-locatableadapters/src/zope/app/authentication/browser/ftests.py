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
"""Functional tests

$Id$
"""
import unittest

def test_suite():
    from zope.app.testing import functional
    return unittest.TestSuite((
        functional.FunctionalDocFileSuite('principalfolder.txt'),
        functional.FunctionalDocFileSuite('groupfolder.txt'),
        functional.FunctionalDocFileSuite(
            'group_searching_with_empty_string.txt'),
        functional.FunctionalDocFileSuite('special-groups.txt'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

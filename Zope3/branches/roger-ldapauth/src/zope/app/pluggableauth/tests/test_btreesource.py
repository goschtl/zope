##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Pluggable Auth Tests

$Id: test_source.py 25177 2004-06-02 13:17:31Z jim $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.testing.doctestunit import DocTestSuite
from zope.app.tests.placelesssetup import setUp, tearDown


def test_suite():
    t1 = DocTestSuite('zope.app.pluggableauth.btreesource',
                      setUp=setUp, tearDown=tearDown)
    return TestSuite((t1,))


if __name__=='__main__':
    main(defaultTest='test_suite')
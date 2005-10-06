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
"""Functional tests for i18n versions of several content objects.

$Id$
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.app.testing.functional import FunctionalDocFileSuite


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(FunctionalDocFileSuite("i18nfile.txt"))
    suite.addTest(FunctionalDocFileSuite("i18nimage.txt"))
    return suite
